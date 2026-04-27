from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from database import SessionLocal
from models import Formacao

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
@router.get("/api/formacoes")
def listar(db: Session = Depends(get_db)):
    
    dados = db.query(Formacao)\
    .order_by(Formacao.data_termino.desc())\
    .all()

    return [
        {
            "id": f.id,
            "descricao": f.descricao,
            "data_termino": f.data_termino,
            "carga_horaria": f.carga_horaria,
            "modalidade": f.modalidade,
            "eixo": f.eixo
        }
        for f in dados
    ]
  
@router.post("/api/formacao")
def criar(dados: dict, db: Session = Depends(get_db)):

    existe = db.query(Formacao).filter(
        Formacao.descricao == dados["descricao"],
        Formacao.data_termino == dados["data_termino"]
    ).first()

    if existe:
        return {"erro": "Formação já cadastrada"}

    try:
        nova = Formacao(**dados)
        db.add(nova)
        db.commit()
        return {"ok": True}
    except IntegrityError:
        db.rollback()
        return {"erro": "Erro ao salvar (possível duplicidade)"}

@router.put("/api/formacao/{id}")
def atualizar(id: int, dados: dict, db: Session = Depends(get_db)):

    f = db.query(Formacao).get(id)

    if not f:
        return {"erro": "Não encontrado"}

    try:
        for k, v in dados.items():
            setattr(f, k, v)

        db.commit()
        return {"ok": True}
    except IntegrityError:
        db.rollback()
        return {"erro": "Duplicidade ao atualizar"}

@router.delete("/api/formacao/{id}")
def deletar(id: int, db: Session = Depends(get_db)):

    f = db.query(Formacao).get(id)

    if not f:
        return {"erro": "Não encontrado"}

    db.delete(f)
    db.commit()

    return {"ok": True}
@router.get("/api/enums")
def enums():
    return {
        "modalidade": ["presencial", "online", "hibrido"],
        "eixo": [
            "Ambientação Institucional/Formação Inicial",
            "Gestão do Trabalho/Saúde Mental e Bem Estar",
            "Qualificação da Prática Socioeducativa Temas Transversais"
        ]
    }
















