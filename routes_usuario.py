from fastapi import APIRouter, Depends, Form
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Usuario
from passlib.context import CryptContext
from security import criar_token

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
# LOGIN (JWT)
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

    token = criar_token({
        "sub": user.username,
        "perfil": user.perfil
    })

    return {
        "ok": True,
        "token": token,
        "perfil": user.perfil,
        "username": user.username
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

    # validação básica
    if not dados.get("username") or not dados.get("senha") or not dados.get("perfil"):
        return {"erro": "Preencha todos os campos"}

    # verifica duplicidade
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
        # atualiza perfil
        if dados.get("perfil"):
            u.perfil = dados["perfil"]

        # atualiza senha (se enviada)
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
