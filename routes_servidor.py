from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Servidor, Cargo
from sqlalchemy.exc import IntegrityError

router = APIRouter()

# ===============================
# DB
# ===============================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ===============================
# LISTAR
# ===============================
@router.get("/api/servidores")
def listar(db: Session = Depends(get_db)):
    dados = db.query(Servidor).join(Cargo).all()

    return [
        {
            "matricula": s.matricula,
            "nome": s.nome,
            "cargo": s.cargo.descricao if s.cargo else None
        }
        for s in dados
    ]

# ===============================
# LISTAR CARGOS (dropdown)
# ===============================
@router.get("/api/cargos")
def listar_cargos(db: Session = Depends(get_db)):
    return db.query(Cargo).order_by(Cargo.descricao).all()

# ===============================
# CRIAR
# ===============================
@router.post("/api/servidor")
def criar(dados: dict, db: Session = Depends(get_db)):
    try:
        cargo = db.query(Cargo).filter_by(id=dados["cargo_id"]).first()

        novo = Servidor(
            matricula=dados["matricula"],
            nome=dados["nome"],
            cargo_id=cargo.id if cargo else None
        )

        db.add(novo)
        db.commit()

        return {"ok": True}

    except IntegrityError:
        db.rollback()
        return {"erro": "Matrícula já existe"}

# ===============================
# ATUALIZAR
# ===============================
@router.put("/api/servidor/{matricula}")
def atualizar(matricula: str, dados: dict, db: Session = Depends(get_db)):

    s = db.query(Servidor).get(matricula)

    if not s:
        return {"erro": "Não encontrado"}

    try:
        s.nome = dados["nome"]
        s.cargo_id = dados["cargo_id"]

        db.commit()
        return {"ok": True}

    except Exception as e:
        db.rollback()
        return {"erro": str(e)}

