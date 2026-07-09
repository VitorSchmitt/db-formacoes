from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database import get_db
# Certifique-se de ajustar o caminho correto da importação do seu modelo
from estagiario.model_acompanhamento import FrequenciaEstagio 
from schemas import FrequenciaEstagioCreate, FrequenciaEstagioUpdate

router = APIRouter(prefix="/api/frequencia_estagio", tags=["Frequências de Estágio"])

@router.get("/", response_model=List[dict])
def listar_frequencias(db: Session = Depends(get_db)):
    frequencias = db.query(FrequenciaEstagio).all()
    return [
        {
            "id": f.id,
            "contrato_id": f.contrato_id,
            "numero_contrato": f.contrato.numero_contrato if f.contrato else "Não informado",
            "competencia": f.competencia.strftime("%m-%Y"),
            "dias": f.dias,
            "horas_realizadas": float(f.horas_realizadas), # Convertido para float para o JSON
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
    
    nova = FrequenciaEstagio(**dados.model_dump())
    db.add(nova)
    db.commit()
    return {"mensagem": "Frequência cadastrada com sucesso"}

@router.put("/{id}")
def atualizar_frequencia(id: int, dados: FrequenciaEstagioUpdate, db: Session = Depends(get_db)):
    frequencia = db.query(FrequenciaEstagio).filter(FrequenciaEstagio.id == id).first()
    if not frequencia:
        raise HTTPException(status_code=404, detail="Frequência não encontrada")
    
    # Se estiver alterando a competência, verifica se não vai gerar duplicidade
    if dados.competencia:
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

    # Atualiza apenas os campos enviados
    dados_atualizados = dados.model_dump(exclude_unset=True)
    for key, value in dados_atualizados.items():
        setattr(frequencia, key, value)
        
    db.commit()
    return {"mensagem": "Frequência atualizada com sucesso"}
