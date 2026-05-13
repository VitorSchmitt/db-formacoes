from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from database import SessionLocal
from models import Participacao, Formacao

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
    request: Request
):
    return templates.TemplateResponse(
        "certificados.html",
        {
            "request": request
        }
    )


# =========================
# FORMAÇÕES
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
# APTOS AO CERTIFICADO
# =========================
@router.get("/api/certificados/{formacao_id}")
def listar_aptos(
    formacao_id: int,
    db: Session = Depends(get_db)
):

    participacoes = (
        db.query(Participacao)
        .join(Formacao)
        .filter(
            Participacao.formacao_id == formacao_id
        )
        .all()
    )

    resultado = []

    for p in participacoes:

        carga_total = p.formacao.carga_horaria or 0
        carga_realizada = p.aproveitamento or 0

        percentual = 0

        if carga_total > 0:

            percentual = round(
                (carga_realizada / carga_total) * 100,
                2
            )

        if percentual >= 75:

            resultado.append({
                "participacao_id": p.id,
                "matricula": p.matricula,
                "servidor": p.servidor.nome,
                "formacao": p.formacao.descricao,
                "carga_total": carga_total,
                "carga_realizada": carga_realizada,
                "percentual": percentual
            })

    return resultado
