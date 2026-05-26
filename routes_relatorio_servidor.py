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
    Participacao
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
        {"request": request}
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
            Servidor.matricula ==
            matricula
        )

        .first()

    )

    if not servidor:

        return {
            "servidor":"",
            "matricula":"",
            "total_horas":0,
            "formacoes":[]
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

    resultado=[]

    total_horas=0

    for p in participacoes:

        f = p.formacao

        carga = (
            f.carga_horaria or 0
        )

        total_horas += carga

        resultado.append({

            "formacao":
                f.descricao,

            "carga_horaria":
                carga,

            "data_fim":
                str(f.data_termino),

            "modalidade":
                str(f.modalidade)

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
    matricula:str,
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

    arquivo="relatorio.pdf"

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

    tabela=[[
        "Formação",
        "CH",        
        "Término"]]

    total=0

    for p in participacoes:

        f = p.formacao

        carga = (
            f.carga_horaria or 0
        )

        total += carga

        tabela.append([

            f.descricao,

            str(carga),

            str(
                f.data_termino
            )

        ])

    tabela.append([
        "Total",        
        str(total)
    ])

    tabela_pdf=Table(
        tabela,
        colWidths=[
            12*cm,
            1*cm,            
            3*cm
        ]
    )

    tabela_pdf.setStyle(

    TableStyle([

        # cabeçalho
        (
            'BACKGROUND',
            (0,0),
            (-1,0),
            colors.lightgrey
        ),

        (
            'FONTNAME',
            (0,0),
            (-1,0),
            'Helvetica-Bold'
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

        # alinhamento geral
        (
            'ALIGN',
            (0,0),
            (0,-1),
            'LEFT'
        ),

        (
            'ALIGN',
            (2,0),
            (2,-1),
            'CENTER'
        ),

        # CH alinhada à direita
        (
            'ALIGN',
            (1,1),
            (1,-1),
            'RIGHT'
        ),

        # linha total
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
        arquivo,
        filename=f"{servidor.nome}.pdf"
    )
