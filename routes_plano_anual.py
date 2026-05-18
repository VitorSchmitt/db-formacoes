from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from database import SessionLocal
from models import PlanoAnual

router = APIRouter()


# conexão com banco
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# =========================
# LISTAR
# =========================
@router.get("/api/plano_anual")
def listar_planos(db: Session = Depends(get_db)):

    dados = (
        db.query(PlanoAnual)
        .order_by(
            PlanoAnual.ano.desc(),
            PlanoAnual.eixo
        )
        .all()
    )

    return [
        {
            "id": p.id,
            "ano": p.ano,
            "eixo": p.eixo,
            "objetivo": p.objetivo,
            "ementa": p.ementa,
            "ativo": p.ativo,
            "criado_em": p.criado_em
        }
        for p in dados
    ]


# =========================
# BUSCAR POR ID
# =========================
@router.get("/api/plano_anual/{id}")
def buscar_plano(
    id: int,
    db: Session = Depends(get_db)
):

    plano = (
        db.query(PlanoAnual)
        .filter(PlanoAnual.id == id)
        .first()
    )

    if not plano:
        raise HTTPException(
            status_code=404,
            detail="Plano não encontrado"
        )

    return {
        "id": plano.id,
        "ano": plano.ano,
        "eixo": plano.eixo,
        "objetivo": plano.objetivo,
        "ementa": plano.ementa,
        "ativo": plano.ativo
    }


# =========================
# CADASTRAR
# =========================
@router.post("/api/plano_anual")
def cadastrar(
    dados: dict,
    db: Session = Depends(get_db)
):

    try:

        novo = PlanoAnual(
            ano=dados["ano"],
            eixo=dados["eixo"],
            objetivo=dados.get("objetivo"),
            ementa=dados.get("ementa")
        )

        db.add(novo)
        db.commit()
        db.refresh(novo)

        return {
            "sucesso": True,
            "mensagem": "Plano cadastrado"
        }

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=400,
            detail="Erro ao salvar plano"
        )


# =========================
# ALTERAR
# =========================
@router.put("/api/plano_anual/{id}")
def alterar(
    id: int,
    dados: dict,
    db: Session = Depends(get_db)
):

    plano = (
        db.query(PlanoAnual)
        .filter(
            PlanoAnual.id == id
        )
        .first()
    )

    if not plano:
        raise HTTPException(
            status_code=404,
            detail="Plano não encontrado"
        )

    plano.ano = dados["ano"]
    plano.eixo = dados["eixo"]
    plano.objetivo = dados.get("objetivo")
    plano.ementa = dados.get("ementa")

    db.commit()

    return {
        "sucesso": True,
        "mensagem": "Plano atualizado"
    }


# =========================
# ATIVAR/DESATIVAR
# =========================
@router.put("/api/plano_anual/status/{id}")
def alterar_status(
    id: int,
    db: Session = Depends(get_db)
):

    plano = (
        db.query(PlanoAnual)
        .filter(
            PlanoAnual.id == id
        )
        .first()
    )

    if not plano:
        raise HTTPException(
            status_code=404,
            detail="Plano não encontrado"
        )

    plano.ativo = not plano.ativo

    db.commit()

    return {
        "sucesso": True,
        "ativo": plano.ativo
    }
