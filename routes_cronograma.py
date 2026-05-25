from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from database import SessionLocal
from models import PlanoAnual

from tempfile import NamedTemporaryFile
from datetime import date

router = APIRouter()


# ==========================
# BANCO
# ==========================

def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


# ==========================
# FORMATA PERÍODO
# ==========================

def periodo_formatado(formacao):

    if not formacao.data_inicio:
        return formacao.periodo or ""

    inicio = formacao.data_inicio.strftime("%B")

    if (
        formacao.data_termino
        and
        formacao.data_inicio.month
        !=
        formacao.data_termino.month
    ):

        fim = formacao.data_termino.strftime("%B")

        return f"{inicio} a {fim}"

    return inicio


# ==========================
# DADOS CRONOGRAMA
# ==========================

@router.get("/api/cronograma/{ano}")

def cronograma(
    ano: int,
    db: Session = Depends(get_db)
):

    planos = (

        db.query(PlanoAnual)

        .filter(
            PlanoAnual.ano == ano,
            PlanoAnual.ativo == True
        )

        .order_by(
            PlanoAnual.eixo
        )

        .all()
    )

    resultado = []

    for plano in planos:

        formacoes = sorted(
            plano.formacoes,
            key=lambda x:
                x.data_inicio
                or date.max
        )

        for f in formacoes:

            resultado.append({

                "periodo":
                    periodo_formatado(f),

                "descricao":
                    f.descricao,

                "eixo":
                    plano.eixo,

                "carga_horaria":
                    f.carga_horaria,

                "publico":
                    f.publico_alvo,

                "investimento":
                    float(
                        f.investimento or 0
                    ),

                "status":
                    f.status

            })

    return resultado
