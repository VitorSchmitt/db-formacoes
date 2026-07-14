from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from typing import List
from database import get_db


# Certifique-se de ajustar o caminho correto da importação do seu modelo
from estagiario.model_acompanhamento import FrequenciaEstagio
from estagiario.model_estagiario import ContratoEstagio
from schemas import FrequenciaEstagioCreate, FrequenciaEstagioUpdate

router = APIRouter(prefix="/api/frequencia_estagio", tags=["Frequências de Estágio"])

@router.get("/", response_model=List[dict])
def listar_frequencias(
    request: Request,
    db: Session = Depends(get_db)
):
    # 1. Recupera os dados do usuário guardados na sessão (Cookie)
    usuario_logado = request.session.get("user")
    
    if not usuario_logado:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não autenticado no sistema."
        )
    
    usuario_logado = request.session.get("user")    
    perfil = usuario_logado.get("perfil")
    matricula = usuario_logado.get("matricula")
    
    query = db.query(FrequenciaEstagio).join(
        ContratoEstagio,
        FrequenciaEstagio.contrato_id == ContratoEstagio.id
    )
    
    if perfil == "operadorIV":
        query = query.filter(
            ContratoEstagio.supervisor_matricula == matricula
        )
    frequencias = query.all()
    
    return [
        {
            "id": f.id,
            "contrato_id": f.contrato_id,
            "numero_contrato": f.contrato.numero_contrato if f.contrato else "Não informado",
            "competencia": f.competencia.strftime("%Y-%m"),
            "dias": f.dias,
            "horas_realizadas": float(f.horas_realizadas),
            "observacao": f.observacao
        }
        for f in frequencias
    ]

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
