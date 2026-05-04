from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload
from database import SessionLocal
from models import Servidor, Cargo
from sqlalchemy.exc import IntegrityError
from schemas import ServidorCreate, ServidorUpdate

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto") 

router = APIRouter()

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
    dados = db.query(Servidor)\
        .options(joinedload(Servidor.cargo))\
        .order_by(Servidor.nome)\
        .all()

    return [
        {
            "matricula": s.matricula,
            "nome": s.nome,
            "cargo": s.cargo.descricao if s.cargo else None,
            "cargo_id": s.cargo_id
        }
        for s in dados
    ]

# ===============================
# CARGOS
# ===============================
@router.get("/api/cargos")
def listar_cargos(db: Session = Depends(get_db)):
    return db.query(Cargo).order_by(Cargo.descricao).all()

# ===============================
# CRIAR
# ===============================
@router.post("/api/usuario")
def criar(dados: dict, db: Session = Depends(get_db)):

    if not dados.get("username") or not dados.get("senha") or not dados.get("perfil"):
        return {"erro": "Preencha todos os campos"}

    try:
        senha_hash = pwd_context.hash(dados["senha"])

        novo = Usuario(
            username=dados["username"],
            senha=senha_hash,
            perfil=dados["perfil"]
        )

        db.add(novo)
        db.commit()

        return {"ok": True}

    except Exception as e:
        db.rollback()
        return {"erro": str(e)}

# ===============================
# ATUALIZAR
# ===============================
@router.put("/api/servidor/{matricula}")
def atualizar(matricula: str, dados: ServidorUpdate, db: Session = Depends(get_db)):

    s = db.get(Servidor, matricula)

    if not s:
        return {"erro": "Não encontrado"}

    cargo = db.get(Cargo, dados.cargo_id)

    if not cargo:
        return {"erro": "Cargo inválido"}

    try:
        s.nome = dados.nome
        s.cargo_id = dados.cargo_id

        db.commit()
        return {"ok": True}

    except Exception as e:
        db.rollback()
        return {"erro": str(e)}
