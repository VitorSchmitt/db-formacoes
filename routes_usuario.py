from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from passlib.context import CryptContext

from database import SessionLocal
from models import Usuario, Servidor
from schemas import UsuarioCreate

router = APIRouter()

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

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
# LISTAR USUÁRIOS
# ===============================
@router.get("/api/usuarios")
def listar_usuarios(db: Session = Depends(get_db)):

    dados = (
        db.query(Usuario)
        .order_by(Usuario.username)
        .all()
    )

    return [
    {
        "id": u.id,
        "matricula": u.matricula,
        "username": u.username,
        "perfil": u.perfil,
        "ativo": u.ativo,
        "email": u.email,
        "criado_em": u.criado_em,
        "ultimo_login": u.ultimo_login
    }
    for u in dados
]


# ===============================
# CRIAR
# ===============================
@router.post("/api/usuario")
def criar_usuario(
    dados: UsuarioCreate,
    db: Session = Depends(get_db)
):

    try:

        servidor = (
            db.query(Servidor)
            .filter(
                Servidor.matricula == dados.matricula
            )
            .first()
        )

        if not servidor:
            return {
                "erro": "Servidor não encontrado"
            }


        existe = (
            db.query(Usuario)
            .filter(
                Usuario.username == dados.username
            )
            .first()
        )

        if existe:
            return {
                "erro": "Usuário já existe"
            }


        senha_hash = pwd_context.hash(
            dados.senha
        )


        novo = Usuario(
            matricula=dados.matricula,
            username=dados.username,
            senha=senha_hash,
            perfil=dados.perfil,
            email=dados.email,
            ativo=True
        )


        db.add(novo)
        db.commit()


        return {
            "ok": True
        }


    except IntegrityError:

        db.rollback()

        return {
            "erro": "Registro duplicado"
        }


    except Exception as e:

        db.rollback()

        return {
            "erro": str(e)
        }

# ===============================
# ATUALIZAR
# ===============================
@router.put("/api/usuario/{id}")
def atualizar_usuario(
    id:int,
    dados:UsuarioCreate,
    db:Session=Depends(get_db)
):

    usuario = (
        db.query(Usuario)
        .filter(
            Usuario.id == id
        )
        .first()
    )

    if not usuario:
        return {
            "erro":"Usuário não encontrado"
        }

    try:

        usuario.matricula = dados.matricula
        usuario.username = dados.username
        usuario.perfil = dados.perfil
        usuario.email = dados.email
        if dados.senha:
            usuario.senha = pwd_context.hash(
                dados.senha
            )

        db.commit()

        return {
            "ok":True
        }

    except Exception as e:

        db.rollback()

        return {
            "erro":str(e)
        }


# ===============================
# ATIVAR / DESATIVAR
# ===============================
@router.put("/api/usuario/status/{id}")
def alterar_status(
    id:int,
    db:Session=Depends(get_db)
):

    usuario = (
        db.query(Usuario)
        .filter(
            Usuario.id==id
        )
        .first()
    )

    if not usuario:
        return {
            "erro":"Usuário não encontrado"
        }

    usuario.ativo = not usuario.ativo

    db.commit()

    return {
        "ok":True,
        "ativo":usuario.ativo
    }


# ===============================
# "EXCLUIR" (INATIVAR)
# ===============================
@router.delete("/api/usuario/{id}")
def inativar_usuario(
    id:int,
    db:Session=Depends(get_db)
):

    usuario = (
        db.query(Usuario)
        .filter(
            Usuario.id==id
        )
        .first()
    )

    if not usuario:
        return {
            "erro":"Usuário não encontrado"
        }

    try:

        usuario.ativo=False

        db.commit()

        return {
            "ok":True
        }

    except Exception as e:

        db.rollback()

        return {
            "erro":str(e)
        }
