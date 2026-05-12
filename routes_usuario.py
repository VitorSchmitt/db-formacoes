from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from passlib.hash import bcrypt
from datetime import datetime

from database import get_db
from models import Usuario

router = APIRouter()

# =====================================================
# LISTAR USUÁRIOS
# =====================================================
@router.get("/api/usuarios")
def listar_usuarios(db: Session = Depends(get_db)):

    usuarios = (
        db.query(Usuario)
        .order_by(Usuario.username)
        .all()
    )

    return [
        {
            "id": u.id,
            "username": u.username,
            "perfil": u.perfil,
            "email": u.email,
            "ativo": u.ativo,
            "criado_em": (
                u.criado_em.strftime("%Y-%m-%d %H:%M")
                if u.criado_em else None
            ),
            "ultimo_login": (
                u.ultimo_login.strftime("%Y-%m-%d %H:%M")
                if u.ultimo_login else None
            )
        }
        for u in usuarios
    ]


# =====================================================
# CRIAR USUÁRIO
# =====================================================
@router.post("/api/usuario")
def criar_usuario(
    dados: dict,
    db: Session = Depends(get_db)
):

    username = dados.get("username", "").strip()
    senha = dados.get("senha", "").strip()
    perfil = dados.get("perfil", "").strip()
    email = dados.get("email")

    # -------------------------
    # VALIDAÇÕES
    # -------------------------
    if not username:
        return JSONResponse(
            status_code=400,
            content={"erro": "Usuário obrigatório"}
        )

    if not senha:
        return JSONResponse(
            status_code=400,
            content={"erro": "Senha obrigatória"}
        )

    if not perfil:
        return JSONResponse(
            status_code=400,
            content={"erro": "Perfil obrigatório"}
        )

    existe = (
        db.query(Usuario)
        .filter(Usuario.username == username)
        .first()
    )

    if existe:
        return JSONResponse(
            status_code=400,
            content={"erro": "Usuário já existe"}
        )

    if email:

        existe_email = (
            db.query(Usuario)
            .filter(Usuario.email == email)
            .first()
        )

        if existe_email:
            return JSONResponse(
                status_code=400,
                content={"erro": "E-mail já cadastrado"}
            )

    # -------------------------
    # CRIAR
    # -------------------------
    usuario = Usuario(
        username=username,
        senha=bcrypt.hash(senha),
        perfil=perfil,
        email=email,
        ativo=True,
        criado_em=datetime.utcnow()
    )

    db.add(usuario)

    db.commit()

    return {
        "ok": True,
        "mensagem": "Usuário criado com sucesso"
    }


# =====================================================
# EDITAR USUÁRIO
# =====================================================
@router.put("/api/usuario/{id}")
def editar_usuario(
    id: int,
    dados: dict,
    db: Session = Depends(get_db)
):

    usuario = (
        db.query(Usuario)
        .filter(Usuario.id == id)
        .first()
    )

    if not usuario:
        return JSONResponse(
            status_code=404,
            content={"erro": "Usuário não encontrado"}
        )

    username = dados.get("username", "").strip()
    perfil = dados.get("perfil", "").strip()
    email = dados.get("email")
    senha = dados.get("senha", "").strip()

    # -------------------------
    # VALIDAÇÕES
    # -------------------------
    if not username:
        return JSONResponse(
            status_code=400,
            content={"erro": "Usuário obrigatório"}
        )

    if not perfil:
        return JSONResponse(
            status_code=400,
            content={"erro": "Perfil obrigatório"}
        )

    existe = (
        db.query(Usuario)
        .filter(
            Usuario.username == username,
            Usuario.id != id
        )
        .first()
    )

    if existe:
        return JSONResponse(
            status_code=400,
            content={"erro": "Usuário já existe"}
        )

    if email:

        existe_email = (
            db.query(Usuario)
            .filter(
                Usuario.email == email,
                Usuario.id != id
            )
            .first()
        )

        if existe_email:
            return JSONResponse(
                status_code=400,
                content={"erro": "E-mail já cadastrado"}
            )

    # -------------------------
    # ATUALIZAR
    # -------------------------
    usuario.username = username
    usuario.perfil = perfil
    usuario.email = email

    # Atualiza senha somente se informada
    if senha:
        usuario.senha = bcrypt.hash(senha)

    db.commit()

    return {
        "ok": True,
        "mensagem": "Usuário atualizado com sucesso"
    }


# =====================================================
# ALTERAR STATUS
# =====================================================
@router.put("/api/usuario/{id}/status")
def alterar_status(
    id: int,
    dados: dict,
    db: Session = Depends(get_db)
):

    usuario = (
        db.query(Usuario)
        .filter(Usuario.id == id)
        .first()
    )

    if not usuario:
        return JSONResponse(
            status_code=404,
            content={"erro": "Usuário não encontrado"}
        )

    usuario.ativo = dados.get("ativo", True)

    db.commit()

    return {
        "ok": True,
        "mensagem": "Status atualizado com sucesso"
    }
