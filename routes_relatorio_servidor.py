from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from reportlab.lib.units import cm
from reportlab.lib import colors

from reportlab.platypus import (
    Paragraph,
    Spacer,
    Table
)

from reportlab.lib.styles import getSampleStyleSheet

from pdf_utils import (
    adicionar_cabecalho,
    criar_documento_pdf,
    aplicar_estilo_tabela,
    adicionar_data_emissao,
    obter_estilo_tabela
)

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

    doc = criar_documento_pdf(arquivo)

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
    
    estilo_esquerda = obter_estilo_tabela()    
    estilo_direita = obter_estilo_tabela()
    estilo_direita.alignment = 2
        
    
    
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
    
    aplicar_estilo_tabela(
    tabela_pdf,
        estilos_extras=[
            ("ALIGN", (1, 0), (2, -1), "RIGHT"),
            ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
            ("BACKGROUND", (0, -1), (-1, -1), colors.lightgrey),
            ("LEADING", (0, 0), (-1, -1), 14),
        ]
    )

    elementos.append(
        tabela_pdf
    )


    

    # ==========================
    # DATA DE EMISSÃO
    # ==========================
    
    adicionar_data_emissao(
        elementos,
        estilo_direita
    )  
    
    doc.build(elementos)
    
    return FileResponse(
        arquivo,
        filename=f"{servidor.nome}.pdf"
    )
