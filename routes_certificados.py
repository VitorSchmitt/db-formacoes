from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import SessionLocal

from models import Participacao, Servidor, Formacao

router = APIRouter()

templates = Jinja2Templates(directory="templates")


# =========================
# DATABASE
# =========================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# =========================
# TELA
# =========================
@router.get("/web/certificados")
def tela_certificados(
    request: Request,
    db: Session = Depends(get_db)
):
    return templates.TemplateResponse(
        "certificados.html",
        {
            "request": request
        }
    )


# =========================
# LISTA FORMAÇÕES
# =========================
@router.get("/api/certificados/formacoes")
def listar_formacoes(
    db: Session = Depends(get_db)
):

    dados = (
        db.query(Formacao)
        .filter(Formacao.ativo == True)
        .order_by(Formacao.descricao)
        .all()
    )

    return [
        {
            "id": f.id,
            "descricao": f.descricao
        }
        for f in dados
    ]


# =========================
# SERVIDORES APTOS
# =========================
@router.get("/api/certificados/{formacao_id}")
def listar_aptos(
    formacao_id: int,
    db: Session = Depends(get_db)
):

    participacoes = (
        db.query(
            Participacao,
            Servidor,
            Formacao
        )
        .join(Servidor, Participacao.servidor_id == Servidor.id)
        .join(Formacao, Participacao.formacao_id == Formacao.id)
        .filter(
            Participacao.formacao_id == formacao_id
        )
        .all()
    )

    resultado = []

    for participacao, servidor, formacao in participacoes:

        # =========================
        # CÁLCULO DOS 75%
        # =========================

        carga_total = formacao.carga_horaria or 0
        carga_presenca = participacao.carga_horaria or 0

        percentual = 0

        if carga_total > 0:
            percentual = round(
                (carga_presenca / carga_total) * 100,
                2
            )

        if percentual >= 75:

            resultado.append({
                "participacao_id": participacao.id,
                "servidor": servidor.nome,
                "carga_total": carga_total,
                "carga_presenca": carga_presenca,
                "percentual": percentual
            })

    return resultado
