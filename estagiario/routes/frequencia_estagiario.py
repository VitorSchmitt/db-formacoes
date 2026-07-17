from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session, joinedload

from typing import List

from database import get_db

from estagiario.model_acompanhamento import (
    FrequenciaEstagio,
    AvaliacaoSupervisor
)

from estagiario.model_estagiario import ContratoEstagio

from schemas import (
    FrequenciaEstagioCreate,
    FrequenciaEstagioUpdate
)

router = APIRouter(prefix="/api/frequencia_estagio", tags=["Frequências de Estágio"])

@router.get("/", response_model=List[dict])
def listar_frequencias(
    request: Request,
    db: Session = Depends(get_db)
):

    usuario_logado = request.session.get("user")

    if not usuario_logado:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não autenticado."
        )

    perfil = usuario_logado.get("perfil")
    matricula = usuario_logado.get("matricula")

    query = (
        db.query(
            FrequenciaEstagio,
            AvaliacaoSupervisor.id.label("avaliacao_id")
        )
        .join(
            ContratoEstagio,
            FrequenciaEstagio.contrato_id == ContratoEstagio.id
        )
        .outerjoin(
            AvaliacaoSupervisor,
            AvaliacaoSupervisor.frequencia_id == FrequenciaEstagio.id
        )
        .options(
            joinedload(FrequenciaEstagio.contrato)
            .joinedload(ContratoEstagio.estagiario)
        )
    )

    if perfil == "operadorIV":
        query = query.filter(
            ContratoEstagio.supervisor_matricula == matricula
        )

    resultados = query.order_by(
        FrequenciaEstagio.competencia.desc()
    ).all()

    return [

        {
            "id": freq.id,
            "contrato_id": freq.contrato_id,
            "estagiario_nome": frequencia.contrato.estagiario.nome,
            "numero_contrato": freq.contrato.numero_contrato,
            "competencia": freq.competencia.strftime("%Y-%m"),
            "dias": freq.dias,
            "horas_realizadas": float(freq.horas_realizadas),
            "observacao": freq.observacao,
            "avaliada": avaliacao_id is not None,
            "avaliacao_id": avaliacao_id
        }

        for freq, avaliacao_id in resultados

    ]
@router.get("/{id}")
def buscar_frequencia(
    id: int,
    request: Request,
    db: Session = Depends(get_db)
):

    usuario = request.session.get("user")

    if not usuario:
        raise HTTPException(
            status_code=401,
            detail="Usuário não autenticado."
        )

    perfil = usuario.get("perfil")
    matricula = usuario.get("matricula")


    query = (
        db.query(FrequenciaEstagio)
        .options(
            joinedload(FrequenciaEstagio.avaliacao)
        )
        .join(
            ContratoEstagio,
            FrequenciaEstagio.contrato_id == ContratoEstagio.id
        )
        .filter(
            FrequenciaEstagio.id == id
        )
    )


    if perfil == "operadorIV":
        query = query.filter(
            ContratoEstagio.supervisor_matricula == matricula
        )


    frequencia = query.first()


    if not frequencia:
        raise HTTPException(
            status_code=404,
            detail="Frequência não encontrada."
        )


    return {
        "id": frequencia.id,
        "contrato_id": frequencia.contrato_id,
        "numero_contrato": frequencia.contrato.numero_contrato,
        "competencia": frequencia.competencia.strftime("%Y-%m"),
        "dias": frequencia.dias,
        "horas_realizadas": float(frequencia.horas_realizadas),
        "observacao": frequencia.observacao,
        "avaliacao_id": (
            frequencia.avaliacao.id
            if frequencia.avaliacao
            else None
        )
    }
@router.post("/", status_code=status.HTTP_201_CREATED)
def criar_frequencia(
    dados: FrequenciaEstagioCreate,
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
                detail="Você não possui permissão para registrar frequência neste contrato."
            )

    # ==============================
    # Verifica duplicidade
    # ==============================
    existe = db.query(FrequenciaEstagio).filter(
        FrequenciaEstagio.contrato_id == dados.contrato_id,
        FrequenciaEstagio.competencia == dados.competencia
    ).first()

    if existe:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Já existe um registro de frequência para este contrato nesta competência."
        )

    # ==============================
    # Grava
    # ==============================
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

    return {
        "mensagem": "Frequência cadastrada com sucesso"
    }


@router.put("/{id}")
def atualizar_frequencia(
    id: int,
    dados: FrequenciaEstagioUpdate,
    db: Session = Depends(get_db)
):
    frequencia = db.query(FrequenciaEstagio).filter(
        FrequenciaEstagio.id == id
    ).first()

    if not frequencia:
        raise HTTPException(
            status_code=404,
            detail="Frequência não encontrada"
        )

    # Verifica duplicidade da competência
    if frequencia.avaliacao and dados.competencia:
        raise HTTPException(
            status_code=400,
            detail="Não é possível alterar a competência de uma frequência já avaliada."
        )
    if dados.competencia is not None:
        conflito = db.query(FrequenciaEstagio).filter(
            FrequenciaEstagio.contrato_id == frequencia.contrato_id,
            FrequenciaEstagio.competencia == dados.competencia,
            FrequenciaEstagio.id != id
        ).first()

        if conflito:
            raise HTTPException(
                status_code=400,
                detail="O contrato já possui uma frequência registrada para esta competência."
            )

    # Atualiza somente os campos informados
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

    return {
        "mensagem": "Frequência atualizada com sucesso"
    }
