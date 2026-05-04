from fastapi import APIRouter, Depends, Form
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Usuario
from passlib.context import CryptContext

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

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
# LOGIN
# ===============================
@router.post("/login")
def login(
    username: str = Form(...),
    senha: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(Usuario).filter_by(username=username).first()

    if not user or not pwd_context.verify(senha, user.senha):
        return {"erro": "Usuário ou senha inválidos"}

    return {
        "ok": True,
        "perfil": user.perfil,
        "username": user.username
    }


# ===============================
# LISTAR USUÁRIOS (opcional)
# ===============================
@router.get("/api/usuarios")
def listar(db: Session = Depends(get_db)):
    dados = db.query(Usuario).all()

    return [
        {
            "id": u.id,
            "username": u.username,
            "perfil": u.perfil
        }
        for u in dados
    ]


# ===============================
# CRIAR USUÁRIO
# ===============================
@router.post("/api/usuario")
def criar(dados: dict, db: Session = Depends(get_db)):
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
