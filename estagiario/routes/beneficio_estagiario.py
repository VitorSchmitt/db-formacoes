from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database import get_db

# Ajuste as importações para os novos schemas criados
from estagiario.model_estagiario import BeneficioEstagiario 
from schemas import BeneficioEstagiarioCreate, BeneficioEstagiarioUpdate

# Mantido o prefixo original do seu back-end
router = APIRouter(
    prefix="/api/beneficio_estagiario",
    tags=["Benefícios Estagiário"]
)

@router.get("/", response_model=List[dict])
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

# Usando o schema Create (todos os campos obrigatórios no POST)
@router.post("/", status_code=status.HTTP_201_CREATED)
def criar_beneficio(dados: BeneficioEstagiarioCreate, db: Session = Depends(get_db)):
    existe = db.query(BeneficioEstagiario).filter(BeneficioEstagiario.data_inicio_vigencia == dados.data_inicio_vigencia).first()
    if existe:
        raise HTTPException(status_code=400, detail="Já existe um benefício cadastrado com esta data de vigência.")
    
    # model_dump() substitui o antigo dict() no Pydantic V2
    novo = BeneficioEstagiario(**dados.model_dump())
    db.add(novo)
    db.commit()
    return {"mensagem": "Benefício criado com sucesso"}

# Usando o schema Update (campos opcionais no PUT)
@router.put("/{id}")
def atualizar_beneficio(id: int, dados: BeneficioEstagiarioUpdate, db: Session = Depends(get_db)):
    beneficio = db.query(BeneficioEstagiario).filter(BeneficioEstagiario.id == id).first()
    if not beneficio:
        raise HTTPException(status_code=404, detail="Benefício não encontrado")
        
    conflito = db.query(BeneficioEstagiario).filter(
        BeneficioEstagiario.data_inicio_vigencia == dados.data_inicio_vigencia,
        BeneficioEstagiario.id != id
    ).first()
    if conflito:
        raise HTTPException(status_code=400, detail="Já existe outro registro com esta mesma data de vigência.")
        
    # Atualiza apenas os campos enviados (ignora valores nulos)
    dados_atualizados = dados.model_dump(exclude_unset=True)
    for chave, valor in dados_atualizados.items():
        setattr(beneficio, chave, valor)
        
    db.commit()
    return {"mensagem": "Benefício actualizado com sucesso"}


