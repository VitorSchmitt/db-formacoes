from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from typing import List
from database import get_db


# Certifique-se de ajustar o caminho correto da importação do seu modelo
from estagiario.model_acompanhamento import FrequenciaEstagio
from estagiario.model_estagiario import contrato_estagiario
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
    
    perfil = usuario_logado.get("perfil")
    username_logado = usuario_logado.get("username")

    # 2. Monta a Query base de busca
    query = db.query(FrequenciaEstagio).join(
        ContratoEstagio, 
        FrequenciaEstagio.contrato_id == ContratoEstagio.id
    )
    # 3. Aplica a regra de negócio baseada no perfil
    # Se for um supervisor (no seu caso, mapeado pelo perfil correspondente, ex: operadorIV)
    
    if perfil == "operadorIV":
        # Filtra onde a matrícula do supervisor no contrato é igual ao username de quem logou
        query = query.filter(ContratoEstagio.supervisor_matricula == username_logado)
    
    # Se for outro perfil restrito que você queira limitar, adicione mais condições aqui.
    # Se for 'admin' ou perfis masters, ele pula os filtros e traz .all()

    # Executa a consulta filtrada no banco
    frequencias = query.all()

    # 4. Retorna a lista formatada para o JSON
    return [
        {
            "id": f.id,
            "contrato_id": f.contrato_id,
            "numero_contrato": f.contrato.numero_contrato if f.contrato else "Não informado",
            "competencia": f.competencia.strftime("%Y-%m"),
            "dias": f.dias,
            "horas_realizadas": float(f.horas_realizadas),
            "observacao": f.observacao
        } for f in frequencias
    ]

@router.post("/", status_code=status.HTTP_201_CREATED)
def criar_frequencia(dados: FrequenciaEstagioCreate, db: Session = Depends(get_db)):
    # Validação baseada na UniqueConstraint (Contrato + Competência)
    existe = db.query(FrequenciaEstagio).filter(
        FrequenciaEstagio.contrato_id == dados.contrato_id,
        FrequenciaEstagio.competencia == dados.competencia
    ).first()
    
    if existe:
        raise HTTPException(
            status_code=400, 
            detail="Já existe um registro de frequência para este contrato nesta competência."
        )
    
    nova = FrequenciaEstagio(
        contrato_id=dados.contrato_id,
        competencia=dados.competencia,
        dias=dados.dias,
        horas_realizadas=dados.horas_realizadas,
        observacao=dados.observacao,
    )
    db.add(nova)
    db.commit()
    return {"mensagem": "Frequência cadastrada com sucesso"}


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
