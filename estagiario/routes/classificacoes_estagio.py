from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from model_estagiario import ClassificacaoEstagio
from schemas import ClassificacaoSchema 

router = APIRouter(
    prefix="/api/classificacoes-estagio",
    tags=["Classificações Estágio"]
)

# LISTAGEM (Retorna JSON com o código incluído)
@router.get("/", response_model=List[dict])
def listar(db: Session = Depends(get_db)):
    classificacoes = db.query(ClassificacaoEstagio).order_by(ClassificacaoEstagio.id).all()
    return [
        {
            "id": c.id, 
            "codigo": c.codigo,      # Incluído aqui
            "descricao": c.descricao, 
            "ativo": c.ativo
        } 
        for c in classificacoes
    ]

# SALVAR (POST)
@router.post("/", status_code=status.HTTP_201_CREATED)
def criar(dados: ClassificacaoSchema, db: Session = Depends(get_db)):
    # Verifica se já existe o código (já que ele é UNIQUE no seu Model)
    existe = db.query(ClassificacaoEstagio).filter(ClassificacaoEstagio.codigo == dados.codigo).first()
    if existe:
        raise HTTPException(status_code=400, detail="Este código já está cadastrado.")

    classificacao = ClassificacaoEstagio(
        codigo=dados.codigo,         # Incluído aqui
        descricao=dados.descricao,
        ativo=dados.ativo
    )
    db.add(classificacao)
    db.commit()
    return {"mensagem": "Criado com sucesso"}

# ATUALIZAR (PUT)
@router.put("/{id}")
def atualizar(id: int, dados: ClassificacaoSchema, db: Session = Depends(get_db)):
    classificacao = db.query(ClassificacaoEstagio).filter(ClassificacaoEstagio.id == id).first()
    
    if not classificacao:
        raise HTTPException(status_code=404, detail="Registro não encontrado")
    
    # Verifica duplicidade de código com OUTROS registros ao editar
    codigo_duplicado = db.query(ClassificacaoEstagio).filter(
        ClassificacaoEstagio.codigo == dados.codigo, 
        ClassificacaoEstagio.id != id
    ).first()
    if codigo_duplicado:
        raise HTTPException(status_code=400, detail="Este código já está em uso por outra classificação.")
        
    classificacao.codigo = dados.codigo       # Incluído aqui
    classificacao.descricao = dados.descricao
    classificacao.ativo = dados.ativo
    
    db.commit()
    return {"mensagem": "Atualizado com sucesso"}

