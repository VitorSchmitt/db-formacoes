from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from database import SessionLocal

from models import (
    Facilitador,
    Servidor,
    Formacao
)

from schemas import FacilitadorCreate

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
# LISTAR FACILITADORES
# ===============================
@router.get("/api/facilitador/{formacao_id}")
def listar(
    formacao_id: int,
    db: Session = Depends(get_db)
):

    dados = (

        db.query(Facilitador)

        .join(Servidor)

        .filter(
            Facilitador.formacao_id == formacao_id
        )

        .order_by(
            Servidor.nome
        )

        .all()

    )

    return [

        {
            "id": f.id,
            "matricula": f.matricula,
            "nome": f.servidor.nome
        }

        for f in dados

    ]


# ===============================
# INSERIR
# ===============================
@router.post("/api/facilitador")
def inserir(
    dados: FacilitadorCreate,
    db: Session = Depends(get_db)
):

    servidor = (

        db.query(Servidor)

        .filter(
            Servidor.matricula == dados.matricula
        )

        .first()

    )

    if not servidor:

        raise HTTPException(
            status_code=404,
            detail="Servidor não encontrado"
        )

    formacao = (

        db.query(Formacao)

        .filter(
            Formacao.id == dados.formacao_id
        )

        .first()

    )

    if not formacao:

        raise HTTPException(
            status_code=404,
            detail="Formação não encontrada"
        )

    existe = (

        db.query(Facilitador)

        .filter(
            Facilitador.matricula == dados.matricula,
            Facilitador.formacao_id == dados.formacao_id
        )

        .first()

    )

    if existe:

        return {
            "erro": "Servidor já cadastrado como facilitador nesta formação"
        }

    try:

        novo = Facilitador(

            matricula=dados.matricula,
            formacao_id=dados.formacao_id

        )

        db.add(novo)

        db.commit()

        return {
            "ok": True,
            "mensagem": "Facilitador cadastrado"
        }

    except IntegrityError:

        db.rollback()

        return {
            "erro": "Registro duplicado"
        }


# ===============================
# EXCLUIR
# ===============================
@router.delete("/api/facilitador/{id}")
def excluir(
    id: int,
    db: Session = Depends(get_db)
):

    registro = (

        db.query(Facilitador)

        .filter(
            Facilitador.id == id
        )

        .first()

    )

    if not registro:

        raise HTTPException(
            status_code=404,
            detail="Facilitador não encontrado"
        )

    db.delete(registro)

    db.commit()

    return {
        "ok": True,
        "mensagem": "Facilitador removido"
    }


# ===============================
# FORMAÇÕES DO FACILITADOR
# ===============================
@router.get("/api/facilitador/servidor/{matricula}")
def formacoes_do_facilitador(
    matricula: str,
    db: Session = Depends(get_db)
):

    dados = (

        db.query(Facilitador)

        .join(Formacao)

        .filter(
            Facilitador.matricula == matricula
        )

        .order_by(
            Formacao.data_termino.desc()
        )

        .all()

    )

    return [

        {
            "id": f.id,
            "formacao_id": f.formacao.id,
            "descricao": f.formacao.descricao,
            "data": f.formacao.data_termino
        }

        for f in dados

    ]


@router.get("/api/servidores/matricula/{matricula}")
def buscar_por_matricula(
    matricula: str,
    db: Session = Depends(get_db)
):
    servidor = (
        db.query(Servidor)
        .filter(
            Servidor.matricula == matricula,
            Servidor.ativo == True
        )
        .first()
    )

    if not servidor:
        return {}

    return {
        "matricula": servidor.matricula,
        "nome": servidor.nome
    }
