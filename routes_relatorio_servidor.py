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
from reportlab.lib.styles import (
    getSampleStyleSheet,
    ParagraphStyle
)
from reportlab.lib import colors
from reportlab.lib.units import cm

from datetime import datetime


from database import SessionLocal
from models import (
    Servidor,
    Participacao,
    Formacao
)
from pdf_utils import adicionar_cabecalho

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

@router.get("/web/relatorio_servidor")
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

@router.get("/api/relatorio_servidor")
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
            db.query(Participacao)
            .join(Participacao.formacao)
            .filter(
                Participacao.matricula ==
                servidor.matricula
            )
            .order_by(
                Formacao.data_termino.asc()
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
    "/api/relatorio_servidor/pdf"
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
            db.query(Participacao)
            .join(Participacao.formacao)
            .filter(
                Participacao.matricula ==
                servidor.matricula
            )
            .order_by(
                Formacao.data_termino.asc()
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

    estilos = getSampleStyleSheet()

    elementos = []

    adicionar_cabecalho(
        elementos,        
        "RELATÓRIO DE FORMAÇÕES"
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
    # ESTILOS
    # ==========================
    
    estilo_esquerda = estilos["Normal"]
    
    estilo_direita = ParagraphStyle(
        "direita",
        parent=estilos["Normal"],
        alignment=2   # RIGHT
    ) 
    
    
    
    # ==========================
    # TABELA
    # ==========================
    
    tabela = [[
    
        Paragraph(
            "<b>Formação</b>",
            estilo_esquerda
        ),
    
        Paragraph(
            "<b>CH</b>",
            estilo_direita
        ),
    
        Paragraph(
            "<b>Término</b>",
            estilo_direita
        )
    
    ]]
    
    total = 0
    
    for p in participacoes:
    
        f = p.formacao
        carga = f.carga_horaria or 0
        total += carga
    
        data_fim = ""
    
        if f.data_termino:
            data_fim = f.data_termino.strftime(
                "%d-%m-%Y"
            )
    
        tabela.append([
    
            Paragraph(
                f.descricao,
                estilo_esquerda
            ),
    
            Paragraph(
                f"{carga} hs",
                estilo_direita
            ),
    
            Paragraph(
                data_fim,
                estilo_direita
            )
    
        ])
    
    
    # linha total
    tabela.append([
    
        Paragraph(
            "<b>Total de horas em formações</b>",
            estilo_esquerda
        ),
    
        Paragraph(
            f"<b>{total} hs</b>",
            estilo_direita
        ),
    
        Paragraph(
            "",
            estilo_direita
        )
    
    ])
    
    
    tabela_pdf = Table(
    
        tabela,
    
        colWidths=[
            11.5*cm,
            2.5*cm,
            3*cm
        ]
    
    )
    
    tabela_pdf.setStyle(
    
        TableStyle([
    
            (
                "BACKGROUND",
                (0,0),
                (-1,0),
                colors.lightgrey
            ),
    
            (
                "GRID",
                (0,0),
                (-1,-1),
                1,
                colors.black
            ),
    
            (
                "VALIGN",
                (0,0),
                (-1,-1),
                "MIDDLE"
            ),
    
            (
                "LEADING",
                (0,0),
                (-1,-1),
                14
            ),
    
            (
                "FONTNAME",
                (0,-1),
                (-1,-1),
                "Helvetica-Bold"
            ),
    
            (
                "BACKGROUND",
                (0,-1),
                (-1,-1),
                colors.lightgrey
            )
    
        ])
    
    )

    elementos.append(
        tabela_pdf
    )


    

    # ==========================
    # DATA DE EMISSÃO
    # ==========================
    
    meses = {
    
        1:"janeiro",
        2:"fevereiro",
        3:"março",
        4:"abril",
        5:"maio",
        6:"junho",
        7:"julho",
        8:"agosto",
        9:"setembro",
        10:"outubro",
        11:"novembro",
        12:"dezembro"
    
    }
    
    hoje = datetime.now()
    
    data_emissao = (
        f"{hoje.day} de "
        f"{meses[hoje.month]} de "
        f"{hoje.year}"
    )
    
    elementos.append(
        Spacer(1,30)
    )
    
    
    tabela_data = Table(

        [[
            Paragraph(
                f"Porto Alegre, {data_emissao}",
                estilo_direita
            )
        ]],
    
        colWidths=[17*cm]
    
    )
    
    tabela_data.setStyle(
        
        TableStyle([
        
            (
                "ALIGN",
                (0,0),
                (0,0),
                "RIGHT"
            )
        
        ])
        
    )       
    
    elementos.append(
        tabela_data
    )
    
    doc.build(elementos)
    
    return FileResponse(
        arquivo,
        filename=f"{servidor.nome}.pdf"
    )
