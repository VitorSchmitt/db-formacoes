from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Usuario
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
from pydantic import BaseModel

router = APIRouter()

SECRET_KEY = "segredo_super_forte"
ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ===============================
# SCHEMA
# ===============================
class LoginSchema(BaseModel):
    username: str
    senha: str

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
def login(dados: LoginSchema, db: Session = Depends(get_db)):

    user = db.query(Usuario).filter(Usuario.username == dados.username).first()

    if not user:
        return {"erro": "Usuário ou senha inválidos"}

    if not pwd_context.verify(dados.senha, user.senha):
        return {"erro": "Usuário ou senha inválidos"}

    payload = {
        "sub": user.username,
        "perfil": user.perfil,
        "exp": datetime.utcnow() + timedelta(hours=8)
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    return {
        "ok": True,
        "token": token,
        "perfil": user.perfil
    }
