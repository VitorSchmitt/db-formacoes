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
    user = db.query(Usuario).filter_by(username=username).first()

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
        "username": user.username,
        "perfil": user.perfil
    }


# ===============================
# LISTAR USUÁRIOS
# ===============================
@router.get("/api/usuarios")
def listar(db: Session = Depends(get_db)):
    dados = db.query(Usuario).order_by(Usuario.username).all()

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

    if not all(k in dados for k in ["username", "senha", "perfil"]):
        return {"erro": "Preencha todos os campos"}

    existe = db.query(Usuario).filter_by(username=dados["username"]).first()
    if existe:
        return {"erro": "Usuário já existe"}

    try:
        novo = Usuario(
            username=dados["username"],
            senha=pwd_context.hash(dados["senha"]),
            perfil=dados["perfil"]
        )

        db.add(novo)
        db.commit()

        return {"ok": True}

    except Exception as e:
        db.rollback()
        return {"erro": str(e)}


# ===============================
# ATUALIZAR USUÁRIO
# ===============================
@router.put("/api/usuario/{id}")
def atualizar(id: int, dados: dict, db: Session = Depends(get_db)):

    u = db.get(Usuario, id)

    if not u:
        return {"erro": "Usuário não encontrado"}

    try:
        if dados.get("perfil"):
            u.perfil = dados["perfil"]

        if dados.get("senha"):
            u.senha = pwd_context.hash(dados["senha"])

        db.commit()

        return {"ok": True}

    except Exception as e:
        db.rollback()
        return {"erro": str(e)}


# ===============================
# DELETAR USUÁRIO
# ===============================
@router.delete("/api/usuario/{id}")
def deletar(id: int, db: Session = Depends(get_db)):

    u = db.get(Usuario, id)

    if not u:
        return {"erro": "Usuário não encontrado"}

    try:
        db.delete(u)
        db.commit()

        return {"ok": True}

    except Exception as e:
        db.rollback()
        return {"erro": str(e)}
