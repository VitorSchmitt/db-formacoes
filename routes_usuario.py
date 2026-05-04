from fastapi import APIRouter, Depends, Form
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Usuario
from passlib.context import CryptContext
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto") 

import os
print("ARQUIVOS NA PASTA:", os.listdir())
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

    print("DADOS RECEBIDOS:", dados)

    if not dados.get("username") or not dados.get("senha") or not dados.get("perfil"):
        return {"erro": "Preencha todos os campos"}

    existe = db.query(Usuario).filter_by(username=dados["username"]).first()

    if existe:
        return {"erro": "Usuário já existe"}

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
        print("ERRO:", str(e))
        return {"erro": str(e)}

@router.delete("/api/usuario/{id}")
def deletar(id: int, db: Session = Depends(get_db)):
    u = db.query(Usuario).get(id)

    if not u:
        return {"erro": "Não encontrado"}

    db.delete(u)
    db.commit()

    return {"ok": True}
@router.put("/api/usuario/{id}")
def atualizar(id: int, dados: dict, db: Session = Depends(get_db)):

    u = db.query(Usuario).get(id)

    if not u:
        return {"erro": "Não encontrado"}

    if dados.get("senha"):
        u.senha = pwd_context.hash(dados["senha"])

    u.perfil = dados["perfil"]

    db.commit()

    return {"ok": True}
