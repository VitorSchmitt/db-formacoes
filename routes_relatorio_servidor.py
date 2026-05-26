from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from database import SessionLocal
from models import Servidor, Participacao, Formacao

router = APIRouter()

templates = Jinja2Templates(
    directory="templates"
)

def get_db():

    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


# tela
@router.get("/web/relatorio-servidor")
def tela_relatorio(
    request: Request
):

    return templates.TemplateResponse(
        "relatorio_servidor.html",
        {
            "request": request
        }
    )


# api
@router.get("/api/relatorio-servidor")
def relatorio_servidor(
    servidor_id: int,
    db: Session = Depends(get_db)
):

    servidor = db.query(
        Servidor
    ).filter(
        Servidor.id == servidor_id
    ).first()

    if not servidor:
        return []

    participacoes = (
        db.query(
            Participacao,
            Formacao
        )
        .join(
            Formacao,
            Participacao.formacao_id ==
            Formacao.id
        )
        .filter(
            Participacao.servidor_id ==
            servidor_id
        )
        .all()
    )

    resultado = []

    for p, f in participacoes:

        resultado.append({

            "formacao":
                f.formacao,

            "eixo":
                f.eixo,

            "carga_horaria":
                f.carga_horaria,

            "data_inicio":
                f.data_inicio,

            "data_fim":
                f.data_fim
        })

    return {
        "servidor":
            servidor.nome,

        "formacoes":
            resultado
    }
