from typing import List
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session, joinedload

from database import get_db
# Import correto do Enum do seu projeto
from estagiario.enums import StatusPagamentoEstagioEnum
from estagiario.model_acompanhamento import AvaliacaoSupervisor, FrequenciaEstagio
from estagiario.model_estagiario import ContratoEstagio
from schemas import FrequenciaEstagioCreate, FrequenciaEstagioUpdate

router = APIRouter(prefix="/api/frequencia_estagio", tags=["Frequências de Estágio"])


# =====================================================
# AUXILIAR: Valida usuário logado e permissões
# =====================================================
def obter_usuario_logado(request: Request):
    usuario = request.session.get("user")
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não autenticado."
        )
    return usuario


# =====================================================
# LISTAR FREQUÊNCIAS
# =====================================================
@router.get("/", response_model=List[dict])
def listar_frequencias(
    request: Request,
    db: Session = Depends(get_db)
):
    usuario = obter_usuario_logado(request)
    perfil = usuario.get("perfil")
    matricula = usuario.get("matricula")

    query = (
        db.query(
            FrequenciaEstagio,
            AvaliacaoSupervisor.id.label("avaliacao_id")
        )
        .join(ContratoEstagio, FrequenciaEstagio.contrato_id == ContratoEstagio.id)
        .outerjoin(AvaliacaoSupervisor, AvaliacaoSupervisor.frequencia_id == FrequenciaEstagio.id)
        .options(
            joinedload(FrequenciaEstagio.contrato)
            .joinedload(ContratoEstagio.estagiario)
        )
    )

    if perfil == "operadorIV":
        query = query.filter(ContratoEstagio.supervisor_matricula == matricula)

    resultados = query.order_by(FrequenciaEstagio.competencia.desc()).all()

    return [
        {
            "id": freq.id,
            "contrato_id": freq.contrato_id,
            "estagiario_nome": freq.contrato.estagiario.nome if freq.contrato and freq.contrato.estagiario else "-",
            "numero_contrato": freq.contrato.numero_contrato if freq.contrato else "-",
            "competencia": freq.competencia.strftime("%Y-%m"),
            "dias": freq.dias,
            "horas_realizadas": float(freq.horas_realizadas),
            "observacao": freq.observacao,
            "avaliada": avaliacao_id is not None,
            "avaliacao_id": avaliacao_id
        }
        for freq, avaliacao_id in resultados
    ]


# =====================================================
# BUSCAR FREQUÊNCIA POR ID
# =====================================================
@router.get("/{id}")
def buscar_frequencia(
    id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    usuario = obter_usuario_logado(request)
    perfil = usuario.get("perfil")
    matricula = usuario.get("matricula")

    query = (
        db.query(FrequenciaEstagio)
        .options(joinedload(FrequenciaEstagio.avaliacao))
        .join(ContratoEstagio, FrequenciaEstagio.contrato_id == ContratoEstagio.id)
        .filter(FrequenciaEstagio.id == id)
    )

    if perfil == "operadorIV":
        query = query.filter(ContratoEstagio.supervisor_matricula == matricula)

    frequencia = query.first()

    if not frequencia:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Frequência não encontrada."
        )

    return {
        "id": frequencia.id,
        "contrato_id": frequencia.contrato_id,
        "numero_contrato": frequencia.contrato.numero_contrato if frequencia.contrato else "-",
        "competencia": frequencia.competencia.strftime("%Y-%m"),
        "dias": frequencia.dias,
        "horas_realizadas": float(frequencia.horas_realizadas),
        "observacao": frequencia.observacao,
        "avaliacao_id": frequencia.avaliacao.id if frequencia.avaliacao else None
    }


# =====================================================
# CRIAR FREQUÊNCIA
# =====================================================
@router.post("/", status_code=status.HTTP_201_CREATED)
def criar_frequencia(
    dados: FrequenciaEstagioCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    usuario = obter_usuario_logado(request)
    perfil = usuario.get("perfil")
    matricula = usuario.get("matricula")

    if perfil == "operadorIV":
        contrato = db.query(ContratoEstagio).filter(
            ContratoEstagio.id == dados.contrato_id,
            ContratoEstagio.supervisor_matricula == matricula
        ).first()

        if not contrato:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você não possui permissão para registrar frequência neste contrato."
            )

    existe = db.query(FrequenciaEstagio).filter(
        FrequenciaEstagio.contrato_id == dados.contrato_id,
        FrequenciaEstagio.competencia == dados.competencia
    ).first()

    if existe:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Já existe um registro de frequência para este contrato nesta competência."
        )

    nova = FrequenciaEstagio(
        contrato_id=dados.contrato_id,
        competencia=dados.competencia,
        dias=dados.dias,
        horas_realizadas=dados.horas_realizadas,
        observacao=dados.observacao
    )

    db.add(nova)
    db.commit()
    db.refresh(nova)

    return {"mensagem": "Frequência cadastrada com sucesso."}


# =====================================================
# ATUALIZAR FREQUÊNCIA
# =====================================================
@router.put("/{id}")
def atualizar_frequencia(
    id: int,
    dados: FrequenciaEstagioUpdate,
    request: Request,
    db: Session = Depends(get_db)
):
    usuario = obter_usuario_logado(request)
    perfil = usuario.get("perfil")
    matricula = usuario.get("matricula")

    query = db.query(FrequenciaEstagio).options(
        joinedload(FrequenciaEstagio.avaliacao),
        joinedload(FrequenciaEstagio.pagamento)
    ).filter(FrequenciaEstagio.id == id)

    if perfil == "operadorIV":
        query = query.join(ContratoEstagio).filter(ContratoEstagio.supervisor_matricula == matricula)

    frequencia = query.first()

    if not frequencia:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Frequência não encontrada ou sem permissão de alteração."
        )

    # Trava se a folha desta frequência já estiver fechada
    if frequencia.pagamento and frequencia.pagamento.status == StatusPagamentoEstagioEnum.FECHADA:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A folha desta frequência já foi encerrada."
        )

    # Trava alteração de competência se a frequência já tiver avaliação
    if frequencia.avaliacao and dados.competencia:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não é possível alterar a competência de uma frequência já avaliada."
        )

    # Valida duplicidade da competência caso ela tenha sido alterada
    if dados.competencia is not None:
        conflito = db.query(FrequenciaEstagio).filter(
            FrequenciaEstagio.contrato_id == frequencia.contrato_id,
            FrequenciaEstagio.competencia == dados.competencia,
            FrequenciaEstagio.id != id
        ).first()

        if conflito:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="O contrato já possui uma frequência registrada para esta competência."
            )

    # Atualizações dos campos
    if dados.contrato_id is not None:
        frequencia.contrato_id = dados.contrato_id
    if dados.competencia is not None:
        frequencia.competencia = dados.competencia
    if dados.dias is not None:
        frequencia.dias = dados.dias
    if dados.horas_realizadas is not None:
        frequencia.horas_realizadas = dados.horas_realizadas
    if dados.observacao is not None:
        frequencia.observacao = dados.observacao

    db.commit()
    db.refresh(frequencia)

    return {"mensagem": "Frequência atualizada com sucesso."}


# =====================================================
# EXCLUIR FREQUÊNCIA
# =====================================================
@router.delete("/{id}")
def excluir_frequencia(
    id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    usuario = obter_usuario_logado(request)
    perfil = usuario.get("perfil")
    matricula = usuario.get("matricula")

    query = db.query(FrequenciaEstagio).options(
        joinedload(FrequenciaEstagio.avaliacao),
        joinedload(FrequenciaEstagio.pagamento)
    ).filter(FrequenciaEstagio.id == id)

    if perfil == "operadorIV":
        query = query.join(ContratoEstagio).filter(ContratoEstagio.supervisor_matricula == matricula)

    frequencia = query.first()

    if not frequencia:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Frequência não encontrada ou sem permissão de exclusão."
        )

    # Trava se a folha desta frequência já estiver fechada
    if frequencia.pagamento and frequencia.pagamento.status == StatusPagamentoEstagioEnum.FECHADA:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A folha desta frequência já foi encerrada."
        )

    # Trava frequência avaliada
    if frequencia.avaliacao:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Esta frequência possui avaliação registrada."
        )

    db.delete(frequencia)
    db.commit()

    return {"mensagem": "Frequência excluída com sucesso."}
