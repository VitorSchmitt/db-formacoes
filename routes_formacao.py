from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from database import SessionLocal
from models import Formacao
from fastapi import Query
from sqlalchemy import func


router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/api/formacoes")
def listar(
    busca: str = Query(None),
    pagina: int = 1,
    limite: int = 20,
    db: Session = Depends(get_db)
):

    query = db.query(Formacao)

    # 🔎 filtro por descrição
    if busca:
        query = query.filter(Formacao.descricao.ilike(f"%{busca}%"))

    total = query.count()

    dados = (
        query.order_by(Formacao.data_termino.desc())
        .offset((pagina - 1) * limite)
        .limit(limite)
        .all()
    )

    return {
        "dados": [
            {
                "id": f.id,
                "descricao": f.descricao,                
                "carga_horaria": f.carga_horaria,   
                "data_termino": f.data_termino.strftime("%Y-%m-%d") if f.data_termino else None,
                "modalidade": str(f.modalidade) if f.modalidade else None,
                "eixo": str(f.eixo) if f.eixo else None,
                "ativo": f.ativo
            }
            for f in dados
        ],
        "total": total,
        "total_paginas": (total // limite) + (1 if total % limite else 0)
    }
  
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

from schemas import FormacaoUpdate
from sqlalchemy.exc import IntegrityError

@router.put("/api/formacao/{id}")
def atualizar(id: int, dados: FormacaoUpdate, db: Session = Depends(get_db)):

    f = db.get(Formacao, id)

    if not f:
        return {"erro": "Não encontrado"}

    try:
        for k, v in dados.dict(exclude_unset=True).items():
            setattr(f, k, v)

        db.commit()
        db.refresh(f)

        return {"ok": True}

    except IntegrityError:
        db.rollback()
        return {"erro": "Duplicidade ao atualizar"}

    except Exception as e:
        db.rollback()
        return {"erro": str(e)}  # 👈 agora você vai ver o erro real


@router.patch("/api/formacoes/toggle/{formacao_id}")
def toggle_formacao(
    formacao_id: int,
    db: Session = Depends(get_db)
):

    formacao = db.get(Formacao, formacao_id)

    if not formacao:
        raise HTTPException(
            status_code=404,
            detail="Formação não encontrada"
        )

    formacao.ativo = not formacao.ativo

    db.commit()

    return {
        "ok": True,
        "ativo": formacao.ativo
    }


@router.delete("/api/formacoes/{formacao_id}")
def desativar_formacao(
    formacao_id: int,
    db: Session = Depends(get_db)
):

    formacao = db.get(Formacao, formacao_id)

    if not formacao:
        return {
            "erro": "Formação não encontrada"
        }

    formacao.ativo = False

    db.commit()

    return {
        "ok": True,
        "message": "Formação desativada"
    }




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
















