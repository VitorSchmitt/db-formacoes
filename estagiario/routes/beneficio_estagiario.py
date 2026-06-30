from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database import get_db
# Substitua pelos seus caminhos reais de importação
from models import BeneficioEstagiario 
from schemas import BeneficioEstagiarioSchema

router_beneficio = APIRouter(prefix="/api/beneficios_estagiario", tags=["Benefícios Estagiário"])

@router_beneficio.get("/", response_model=List[dict])
def listar_beneficios(db: Session = Depends(get_db)):
    beneficios = db.query(BeneficioEstagiario).order_by(BeneficioEstagiario.data_inicio_vigencia.desc()).all()
    return [
        {
            "id": b.id,
            "valor_vale_alimentacao": float(b.valor_vale_alimentacao),
            "valor_vale_transporte": float(b.valor_vale_transporte),
            "data_inicio_vigencia": b.data_inicio_vigencia.strftime("%Y-%m-%d")
        } for b in beneficios
    ]

@router_beneficio.post("/", status_code=status.HTTP_201_CREATED)
def criar_beneficio(dados: BeneficioEstagiarioSchema, db: Session = Depends(get_db)):
    existe = db.query(BeneficioEstagiario).filter(BeneficioEstagiario.data_inicio_vigencia == dados.data_inicio_vigencia).first()
    if existe:
        raise HTTPException(status_code=400, detail="Já existe um benefício cadastrado com esta data de vigência.")
    
    novo = BeneficioEstagiario(**dados.model_dump())
    db.add(novo)
    db.commit()
    return {"mensagem": "Benefício criado com sucesso"}

@router_beneficio.put("/{id}")
def atualizar_beneficio(id: int, dados: BeneficioEstagiarioSchema, db: Session = Depends(get_db)):
    beneficio = db.query(BeneficioEstagiario).filter(BeneficioEstagiario.id == id).first()
    if not beneficio:
        raise HTTPException(status_code=404, detail="Benefício não encontrado")
        
    conflito = db.query(BeneficioEstagiario).filter(
        BeneficioEstagiario.data_inicio_vigencia == dados.data_inicio_vigencia,
        BeneficioEstagiario.id != id
    ).first()
    if conflito:
        raise HTTPException(status_code=400, detail="Já existe outro registro com esta mesma data de vigência.")
        
    beneficio.valor_vale_alimentacao = dados.valor_vale_alimentacao
    beneficio.valor_vale_transporte = dados.valor_vale_transporte
    beneficio.data_inicio_vigencia = dados.data_inicio_vigencia
    db.commit()
    return {"mensagem": "Benefício atualizado com sucesso"}
