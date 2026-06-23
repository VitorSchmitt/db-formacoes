from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
# Certifique-se de ajustar os caminhos de importação para a sua estrutura de pastas
from estagiario.model_estagiario import ValorBolsaEstagio 
from schemas import ValorBolsaSchema

router = APIRouter(
    prefix="/api/valores_bolsa_estagio",
    tags=["Valores Bolsa Estágio"]
)

# LISTAGEM (Retorna JSON incluindo dados da classificação se houver o relacionamento)
@router.get("/", response_model=List[dict])
def listar(db: Session = Depends(get_db)):
    valores = db.query(ValorBolsaEstagio).order_by(ValorBolsaEstagio.data_inicio_vigencia.desc()).all()
    
    return [
        {
            "id": v.id,
            "classificacao_id": v.classificacao_id,
            # Tenta pegar o nome/descrição da classificação para exibir na tabela do front
            "classificacao_descricao": v.classificacao.descricao if v.classificacao else "Não informada",
            "valor_hora": float(v.valor_hora),
            "data_inicio_vigencia": v.data_inicio_vigencia.strftime("%Y-%m-%d")
        }
        for v in valores
    ]

# SALVAR (POST)
@router.post("/", status_code=status.HTTP_201_CREATED)
def criar(dados: ValorBolsaSchema, db: Session = Depends(get_db)):
    # Valida a UniqueConstraint composta: mesma classificação na mesma data
    existe = db.query(ValorBolsaEstagio).filter(
        ValorBolsaEstagio.classificacao_id == dados.classificacao_id,
        ValorBolsaEstagio.data_inicio_vigencia == dados.data_inicio_vigencia
    ).first()
    
    if existe:
        raise HTTPException(
            status_code=400, 
            detail="Já existe um valor cadastrado para esta classificação nesta mesma data de vigência."
        )

    novo_valor = ValorBolsaEstagio(
        classificacao_id=dados.classificacao_id,
        valor_hora=dados.valor_hora,
        data_inicio_vigencia=dados.data_inicio_vigencia
    )
    
    db.add(novo_valor)
    db.commit()
    return {"mensagem": "Criado com sucesso"}

# ATUALIZAR (PUT)
@router.put("/{id}")
def atualizar(id: int, dados: ValorBolsaSchema, db: Session = Depends(get_db)):
    valor_bolsa = db.query(ValorBolsaEstagio).filter(ValorBolsaEstagio.id == id).first()
    
    if not valor_bolsa:
        raise HTTPException(status_code=404, detail="Registro não encontrado")
        
    # Valida se a alteração viola a UniqueConstraint composta de OUTRO registro
    conflito = db.query(ValorBolsaEstagio).filter(
        ValorBolsaEstagio.classificacao_id == dados.classificacao_id,
        ValorBolsaEstagio.data_inicio_vigencia == dados.data_inicio_vigencia,
        ValorBolsaEstagio.id != id
    ).first()
    
    if conflito:
        raise HTTPException(
            status_code=400, 
            detail="Já existe outro registro com esta mesma classificação e data de vigência."
        )
        
    valor_bolsa.classificacao_id = dados.classificacao_id
    valor_bolsa.valor_hora = dados.valor_hora
    valor_bolsa.data_inicio_vigencia = dados.data_inicio_vigencia
    
    db.commit()
    return {"mensagem": "Atualizado com sucesso"}
