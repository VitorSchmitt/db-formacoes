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

MESES = {

    1: "janeiro",
    2: "fevereiro",
    3: "março",
    4: "abril",
    5: "maio",
    6: "junho",
    7: "julho",
    8: "agosto",
    9: "setembro",
    10: "outubro",
    11: "novembro",
    12: "dezembro"

}


def periodo_formatado(formacao):

    if not formacao.data_inicio:
        return formacao.periodo or ""

    inicio = MESES[
        formacao.data_inicio.month
    ]

    if (

        formacao.data_termino
        and
        formacao.data_inicio.month
        !=
        formacao.data_termino.month

    ):

        fim = MESES[
            formacao.data_termino.month
        ]

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
        EIXOS = {
        
            "Ambientação Institucional/Formação Inicial":
                "I",
        
            "Gestão do Trabalho/Saúde Mental e Bem Estar":
                "II",
        
            "Qualificação da Prática Socioeducativa Temas Transversais":
                "III"
        
        }
        
        for f in formacoes:
        
            eixo_original = f.eixo or ""

            eixo = EIXOS.get(
                eixo_original,
                eixo_original
            )
        
            resultado.append({
        
                "periodo":
                    periodo_formatado(f),
        
                "descricao":
                    f.descricao,
        
                "eixo":
                    eixo,
        
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
