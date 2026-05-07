from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from database import SessionLocal
from models import Usuario

router = APIRouter()

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/login")
async def login(
    request: Request,
    username: str = Form(...),
    senha: str = Form(...),
    db: Session = Depends(get_db)
):

    user = db.query(Usuario).filter(
        Usuario.username == username
    ).first()

    if not user:
        return JSONResponse(
            status_code=401,
            content={"erro": "Usuário inválido"}
        )

    if not pwd_context.verify(senha, user.senha):
        return JSONResponse(
            status_code=401,
            content={"erro": "Senha inválida"}
        )

    request.session["user"] = {
        "id": user.id,
        "username": user.username,
        "perfil": user.perfil
    }

    return {
        "ok": True,
        "redirect": "/web/dashboard",
        "perfil": user.perfil
    }


@router.get("/logout")
def logout(request: Request):

    request.session.clear()

    return {
        "ok": True,
        "redirect": "/"
    }
