from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from database import SessionLocal
from models import Servidor, Participacao, Formacao
from fastapi.responses import FileResponse
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
    
@router.get("/api/relatorio-servidor/pdf")
def relatorio_servidor_pdf(
    servidor_id: int,
    db: Session = Depends(get_db)
):

    servidor = db.query(
        Servidor
    ).filter(
        Servidor.id == servidor_id
    ).first()

    if not servidor:
        return {"erro":"Servidor não encontrado"}

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

    arquivo = "relatorio_servidor.pdf"

    doc = SimpleDocTemplate(
        arquivo,
        rightMargin=1*cm,
        leftMargin=1*cm,
        topMargin=1*cm,
        bottomMargin=1*cm
    )

    estilos = styles.getSampleStyleSheet()

    elementos=[]

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
        Spacer(1,10)
    )

    tabela=[]

    tabela.append([
        "Formação",
        "Eixo",
        "Carga Horária",
        "Período"
    ])

    total_horas=0

    for p,f in participacoes:

        carga = f.carga_horaria or 0

        total_horas += carga

        periodo = (
            f"{f.data_inicio}"
            f" até "
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
        "Total:",
        str(total_horas)
    ])

    tabela_pdf=Table(
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

            ('BACKGROUND',(0,0),(-1,0),colors.lightgrey),

            ('GRID',(0,0),(-1,-1),1,colors.black),

            ('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),

            ('VALIGN',(0,0),(-1,-1),'MIDDLE'),

            ('BACKGROUND',(-2,-1),(-1,-1),colors.lightgrey)

        ])
    )

    elementos.append(
        tabela_pdf
    )

    doc.build(
        elementos
    )

    return FileResponse(
        arquivo,
        filename=f"{servidor.nome}.pdf"
    )
