from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image
)

from reportlab.lib import colors
from reportlab.lib import styles
from reportlab.lib.units import cm

from datetime import datetime
import os

from database import SessionLocal
from models import (
    Servidor,
    Participacao
)

LOGO = "static/img/logo.png"
FASE = "static/img/fase.png"

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
# CONSULTA
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
            "matricula": "",
            "total_horas": 0,
            "formacoes": []
        }

    participacoes = (

        db.query(
            Participacao
        )

        .filter(
            Participacao.matricula ==
            servidor.matricula
        )

        .all()

    )

    resultado = []

    total_horas = 0

    for p in participacoes:

        f = p.formacao

        carga = (
            f.carga_horaria or 0
        )

        total_horas += carga

        data_fim = ""

        if f.data_termino:

            data_fim = (
                f.data_termino.strftime(
                    "%d-%m-%Y"
                )
            )

        resultado.append({

            "formacao":
                f.descricao,

            "carga_horaria":
                carga,

            "data_fim":
                data_fim,

            "modalidade":
                str(
                    f.modalidade
                )

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
def gerar_pdf(
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
            Participacao
        )

        .filter(
            Participacao.matricula ==
            servidor.matricula
        )

        .all()

    )

    arquivo = "relatorio.pdf"

    doc = SimpleDocTemplate(

        arquivo,

        rightMargin=1*cm,
        leftMargin=1*cm,
        topMargin=1*cm,
        bottomMargin=1*cm

    )

    estilos = (
        styles.getSampleStyleSheet()
    )

    elementos=[]


    # ==========================
    # LOGOS
    # ==========================

    logo_esquerda = ""
    logo_direita = ""

    if os.path.exists(LOGO):

        logo_esquerda = Image(
            LOGO,
            width=5*cm,
            height=2.5*cm
        )

    if os.path.exists(FASE):

        logo_direita = Image(
            FASE,
            width=2.5*cm,
            height=2.5*cm
        )

    tabela_logos = Table(

        [[
            logo_esquerda,
            logo_direita
        ]],

        colWidths=[
            9*cm,
            9*cm
        ]

    )

    tabela_logos.setStyle(

        TableStyle([

            (
                "ALIGN",
                (0,0),
                (0,0),
                "LEFT"
            ),

            (
                "ALIGN",
                (1,0),
                (1,0),
                "RIGHT"
            ),

            (
                "VALIGN",
                (0,0),
                (-1,-1),
                "MIDDLE"
            ),

            (
                "BOTTOMPADDING",
                (0,0),
                (-1,-1),
                10
            )

        ])

    )

    elementos.append(
        tabela_logos
    )

    elementos.append(
        Spacer(1,12)
    )


    # ==========================
    # TÍTULO
    # ==========================

    elementos.append(

        Paragraph(
            "Relatório de Formações",
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


    # ==========================
    # TABELA
    # ==========================

    tabela = [[

        Paragraph(
            "<b>Formação</b>",
            estilos["Normal"]
        ),

        Paragraph(
            "<b>CH</b>",
            estilos["Normal"]
        ),

        Paragraph(
            "<b>Término</b>",
            estilos["Normal"]
        )

    ]]

    total = 0

    for p in participacoes:

        f = p.formacao

        carga = (
            f.carga_horaria or 0
        )

        total += carga

        data_fim = ""

        if f.data_termino:

            data_fim = (
                f.data_termino.strftime(
                    "%d-%m-%Y"
                )
            )

        tabela.append([

            Paragraph(
                f.descricao,
                estilos["Normal"]
            ),

            Paragraph(
                str(carga),
                estilos["Normal"]
            ),

            Paragraph(
                data_fim,
                estilos["Normal"]
            )

        ])


    tabela.append([

        Paragraph(
            "<b>Total</b>",
            estilos["Normal"]
        ),

        Paragraph(
            f"<b>{total}</b>",
            estilos["Normal"]
        ),

        Paragraph(
            "",
            estilos["Normal"]
        )

    ])


    tabela_pdf = Table(

        tabela,

        colWidths=[
            12*cm,
            1.5*cm,
            3*cm
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
                'VALIGN',
                (0,0),
                (-1,-1),
                'MIDDLE'
            ),

            (
                'LEADING',
                (0,0),
                (-1,-1),
                14
            ),

            (
                'ALIGN',
                (0,0),
                (0,-1),
                'LEFT'
            ),

            (
                'ALIGN',
                (1,0),
                (1,-1),
                'RIGHT'
            ),

            (
                'ALIGN',
                (2,0),
                (2,-1),
                'CENTER'
            ),

            (
                'BACKGROUND',
                (0,-1),
                (-1,-1),
                colors.lightgrey
            ),

            (
                'FONTNAME',
                (0,-1),
                (-1,-1),
                'Helvetica-Bold'
            )

        ])

    )

    elementos.append(
        tabela_pdf
    )


    # ==========================
    # DATA DE EMISSÃO
    # ==========================

    data_emissao = datetime.now().strftime(
        "%d-%m-%Y"
    )

    elementos.append(
        Spacer(1,30)
    )

    elementos.append(

        Paragraph(
            f"Porto Alegre, {data_emissao}",
            estilos["Normal"]
        )

    )

    doc.build(
        elementos
    )

    return FileResponse(
        arquivo,
        filename=f"{servidor.nome}.pdf"
    )
