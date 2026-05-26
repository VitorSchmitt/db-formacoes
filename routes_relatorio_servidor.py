from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)

from reportlab.lib import colors
from reportlab.lib import styles
from reportlab.lib.units import cm

from database import SessionLocal
from models import (
    Servidor,
    Participacao,
    Formacao
)

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


# ==========================
# TELA
# ==========================

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


# ==========================
# API CONSULTA
# ==========================

@router.get("/api/relatorio-servidor")
def relatorio_servidor(
    matricula: str,
    db: Session = Depends(get_db)
):

    servidor = (
        db.query(
            Servidor
        )
        .filter(
            Servidor.matricula == matricula
        )
        .first()
    )

    if not servidor:

        return {
            "servidor": "",
            "formacoes": []
        }

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
            servidor.id
        )

        .all()
    )

    resultado = []

    total_horas = 0

    for p, f in participacoes:

        carga = f.carga_horaria or 0

        total_horas += carga

        resultado.append({

            "formacao":
                f.formacao,

            "eixo":
                f.eixo,

            "carga_horaria":
                carga,

            "data_inicio":
                str(f.data_inicio),

            "data_fim":
                str(f.data_fim)

        })

    return {

        "servidor":
            servidor.nome,

        "matricula":
            servidor.matricula,

        "total_horas":
            total_horas,

        "formacoes":
            resultado

    }


# ==========================
# PDF
# ==========================

@router.get(
    "/api/relatorio-servidor/pdf"
)
def relatorio_servidor_pdf(
    matricula: str,
    db: Session = Depends(get_db)
):

    servidor = (

        db.query(
            Servidor
        )

        .filter(
            Servidor.matricula ==
            matricula
        )

        .first()
    )

    if not servidor:

        return {
            "erro":
            "Servidor não encontrado"
        }

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
            servidor.id
        )

        .all()
    )

    nome_arquivo = (
        "relatorio_servidor.pdf"
    )

    doc = SimpleDocTemplate(

        nome_arquivo,

        rightMargin=1*cm,
        leftMargin=1*cm,
        topMargin=1*cm,
        bottomMargin=1*cm

    )

    estilos = (
        styles.getSampleStyleSheet()
    )

    elementos = []

    elementos.append(

        Paragraph(
            "Relatório de Formações do Servidor",
            estilos["Title"]
        )

    )

    elementos.append(
        Spacer(1,15)
    )

    elementos.append(

        Paragraph(
            f"<b>Servidor:</b> {servidor.nome}",
            estilos["Normal"]
        )

    )

    elementos.append(

        Paragraph(
            f"<b>Matrícula:</b> {servidor.matricula}",
            estilos["Normal"]
        )

    )

    elementos.append(
        Spacer(1,15)
    )

    tabela = [[

        "Formação",
        "Eixo",
        "CH",
        "Período"

    ]]

    total_horas = 0

    for p, f in participacoes:

        carga = (
            f.carga_horaria or 0
        )

        total_horas += carga

        periodo = (
            f"{f.data_inicio}"
            " até "
            f"{f.data_fim}"
        )

        tabela.append([

            f.formacao,
            f.eixo,
            str(carga),
            periodo

        ])

    tabela.append([

        "",
        "",
        "Total",

        str(total_horas)

    ])

    tabela_pdf = Table(

        tabela,

        colWidths=[
            8*cm,
            4*cm,
            2*cm,
            5*cm
        ]

    )

    tabela_pdf.setStyle(

        TableStyle([

            (
                'BACKGROUND',
                (0,0),
                (-1,0),
                colors.lightgrey
            ),

            (
                'GRID',
                (0,0),
                (-1,-1),
                1,
                colors.black
            ),

            (
                'FONTNAME',
                (0,0),
                (-1,0),
                'Helvetica-Bold'
            ),

            (
                'VALIGN',
                (0,0),
                (-1,-1),
                'MIDDLE'
            ),

            (
                'BACKGROUND',
                (-2,-1),
                (-1,-1),
                colors.lightgrey
            )

        ])

    )

    elementos.append(
        tabela_pdf
    )

    doc.build(
        elementos
    )

    return FileResponse(

        nome_arquivo,

        filename=
        f"{servidor.nome}.pdf"

    )
