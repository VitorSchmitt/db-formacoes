from datetime import datetime

from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from database import SessionLocal
from models import Usuario

router = APIRouter()

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


# =====================================================
# DATABASE
# =====================================================
def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


# =====================================================
# LOGIN
# =====================================================
@router.post("/login")
async def login(
    request: Request,
    username: str = Form(...),
    senha: str = Form(...),
    db: Session = Depends(get_db)
):

    # =========================================
    # BUSCA USUÁRIO
    # =========================================
    user = (
        db.query(Usuario)
        .filter(Usuario.username == username)
        .first()
    )

    # =========================================
    # USUÁRIO NÃO EXISTE
    # =========================================
    if not user:

        return JSONResponse(
            status_code=401,
            content={
                "erro": "Usuário inválido"
            }
        )

    # =========================================
    # USUÁRIO INATIVO
    # =========================================
    if not user.ativo:

        return JSONResponse(
            status_code=403,
            content={
                "erro": "Usuário inativo"
            }
        )

    # =========================================
    # SENHA INVÁLIDA
    # =========================================
    if not pwd_context.verify(senha, user.senha):

        return JSONResponse(
            status_code=401,
            content={
                "erro": "Senha inválida"
            }
        )

    # =========================================
    # ATUALIZA ÚLTIMO LOGIN
    # =========================================
    user.ultimo_login = datetime.utcnow()

    db.commit()

    # =========================================
    # CRIA SESSÃO
    # =========================================
    request.session["user"] = {
        "id": user.id,
        "username": user.username,
        "perfil": user.perfil
    }

    # =========================================
    # DEFINE DESTINO
    # =========================================
    perfil = user.perfil

    if perfil == "operadorIII":
        destino = "/web/estagiario/estagiarios"

    elif perfil == "operadorII":
        destino = "/web/dashboard"

    elif perfil == "operador":
        destino = "/web/dashboard"

    elif perfil == "custom":
        destino = "/web/dashboard"

    elif perfil == "admin":
        destino = "/web/dashboard"

    else:
        destino = "/"

    # =========================================
    # REDIRECIONA
    # =========================================
    return RedirectResponse(
        url=destino,
        status_code=303
    )



# =====================================================
# LOGOUT
# =====================================================
@router.get("/logout")
def logout(request: Request):

    request.session.clear()

    return {
        "ok": True,
        "redirect": "/"
    }
