from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session, joinedload

from database import get_db
from estagiario.model_acompanhamento import AvaliacaoSupervisor
from estagiario.model_estagiario import ContratoEstagio
from schemas import (
    AvaliacaoSupervisorCreate,
    AvaliacaoSupervisorUpdate
)

router = APIRouter(
    prefix="/api/avaliacao_estagiario",
    tags=["Avaliação do Supervisor"]
)


# ==========================
# LISTAR
# ==========================
@router.get("/")
def listar(
    request: Request,
    db: Session = Depends(get_db),
    limit: int = 100,
    offset: int = 0
):
    # ==============================
    # Usuário logado
    # ==============================
    usuario_logado = request.session.get("user")

    if not usuario_logado:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não autenticado."
        )

    perfil = usuario_logado.get("perfil")
    matricula = usuario_logado.get("matricula")

    # ==============================
    # Consulta base
    # ==============================
    query = (
        db.query(AvaliacaoSupervisor)
        .join(
            ContratoEstagio,
            AvaliacaoSupervisor.contrato_id == ContratoEstagio.id
        )
        .options(
            joinedload(AvaliacaoSupervisor.contrato)
            .joinedload(ContratoEstagio.estagiario)
        )
    )

    # ==============================
    # Restrição do supervisor
    # ==============================
    if perfil == "operadorIV":
        query = query.filter(
            ContratoEstagio.supervisor_matricula == matricula
        )

    resultados = (
        query
        .order_by(AvaliacaoSupervisor.data_avaliacao.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    # ==============================
    # Monta retorno
    # ==============================
    lista_formatada = []

    for av in resultados:
        contrato = av.contrato
        estagiario = contrato.estagiario if contrato else None

        lista_formatada.append({
            "id": av.id,
            "contrato_id": av.contrato_id,
            "data_avaliacao": av.data_avaliacao.isoformat(),
            "avaliacao": av.avaliacao,
            "parecer": av.parecer,
            "numero_contrato": contrato.numero_contrato if contrato else f"Contrato #{av.contrato_id}",
            "estagiario_nome": estagiario.nome if estagiario else "Não informado"
        })

    return lista_formatada


# ==========================
# BUSCAR POR ID
# ==========================
@router.get("/{id}")
def buscar(id: int, db: Session = Depends(get_db)): 

    avaliacao = (
        db.query(AvaliacaoSupervisor)
        .filter(AvaliacaoSupervisor.id == id)
        .first()
    )

    if not avaliacao:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Avaliação não encontrada."
        )

    return avaliacao


# ==========================
# INSERIR
# ==========================
@router.post("/", status_code=status.HTTP_201_CREATED)
def inserir(
    dados: AvaliacaoSupervisorCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    # ==============================
    # Usuário logado
    # ==============================
    usuario_logado = request.session.get("user")

    if not usuario_logado:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não autenticado."
        )

    perfil = usuario_logado.get("perfil")
    matricula = usuario_logado.get("matricula")

    # ==============================
    # Permissão do supervisor
    # ==============================
    if perfil == "operadorIV":

        contrato = db.query(ContratoEstagio).filter(
            ContratoEstagio.id == dados.contrato_id,
            ContratoEstagio.supervisor_matricula == matricula
        ).first()

        if not contrato:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você não possui permissão para avaliar este estagiário."
            )

    # ==============================
    # Grava a avaliação
    # ==============================
    avaliacao = AvaliacaoSupervisor(
        contrato_id=dados.contrato_id,
        data_avaliacao=dados.data_avaliacao,
        avaliacao=dados.avaliacao,
        parecer=dados.parecer
    )

    db.add(avaliacao)
    db.commit()
    db.refresh(avaliacao)

    return avaliacao


# ==========================
# ALTERAR
# ==========================
@router.put("/{id}")
def alterar(
    id: int,
    dados: AvaliacaoSupervisorUpdate,
    db: Session = Depends(get_db)
):

    avaliacao = (
        db.query(AvaliacaoSupervisor)
        .filter(AvaliacaoSupervisor.id == id)
        .first()
    )

    if not avaliacao:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Avaliação não encontrada."
        )

    # Refatorado: Atualização dinâmica usando setattr (evita uma pilha de IFs)
    # Exclui campos não enviados na requisição (útil se o schema aceitar campos opcionais)
    dados_atualizar = dados.model_dump(exclude_unset=True) if hasattr(dados, 'model_dump') else dados.dict(exclude_unset=True)
    
    for chave, valor in dados_atualizar.items():
        setattr(avaliacao, chave, valor)

    db.commit()
    db.refresh(avaliacao)

    return avaliacao


# ==========================
# EXCLUIR
# ==========================
@router.delete("/{id}")
def excluir(
    id: int,
    db: Session = Depends(get_db)
):

    avaliacao = (
        db.query(AvaliacaoSupervisor)
        .filter(AvaliacaoSupervisor.id == id)
        .first()
    )

    if not avaliacao:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Avaliação não encontrada."
        )

    db.delete(avaliacao)
    db.commit()

    return {
        "mensagem": "Avaliação excluída com sucesso."
    }
