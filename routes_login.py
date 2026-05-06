from fastapi import APIRouter, Depends, Form, Request
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
# LOGIN (SESSÃO PURA)
# ===============================
@router.post("/login")
def login(
    request: Request,
    username: str = Form(...),
    senha: str = Form(...),
    db: Session = Depends(get_db)
):

    user = db.query(Usuario).filter(Usuario.username == username).first()

    if not user or not pwd_context.verify(senha, user.senha):
        return {"erro": "Usuário ou senha inválidos"}

    # 🔐 salva sessão
    request.session["user"] = {
        "id": user.id,
        "username": user.username,
        "perfil": user.perfil
    }

    return {
        "ok": True,
        "perfil": user.perfil,
        "username": user.username
    }
