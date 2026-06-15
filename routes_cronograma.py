from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from database import SessionLocal
from models import PlanoAnual

from tempfile import NamedTemporaryFile
from datetime import date

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet


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
        return  ""

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
# EIXOS
# ==========================

EIXOS = {

    "Ambientação Institucional/Formação Inicial":
        "I",

    "Gestão do Trabalho/Saúde Mental e Bem Estar":
        "II",

    "Qualificação da Prática Socioeducativa Temas Transversais":
        "III"

}


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

        eixo_original = plano.eixo or ""

        eixo = EIXOS.get(
            eixo_original,
            eixo_original
        )

        formacoes = sorted(

            plano.formacoes,

            key=lambda x:
                x.data_inicio or date.max

        )

        for f in formacoes:

            resultado.append({

                "data_termino": f.data_termino,

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
    
    resultado.sort(
    key=lambda x: x["data_termino"] or date.max
    )
    return resultado


# ==========================
# PDF CRONOGRAMA
# ==========================

@router.get("/api/cronograma/pdf/{ano}")

def cronograma_pdf(
    ano: int,
    db: Session = Depends(get_db)
):

    dados = cronograma(ano, db)

    with NamedTemporaryFile(
        delete=False,
        suffix=".pdf"
    ) as temp:

        caminho = temp.name

    doc = SimpleDocTemplate(
        caminho,
        pagesize=landscape(A4),
        rightMargin=20,
        leftMargin=20,
        topMargin=20,
        bottomMargin=20
    )

    styles = getSampleStyleSheet()

    elementos = []

    titulo = Paragraph(
        f"<b>Cronograma Anual {ano}</b>",
        styles["Title"]
    )

    elementos.append(titulo)

    elementos.append(
        Spacer(1, 20)
    )

    tabela_dados = [[

        "Período",
        "Formação",
        "Eixo",
        "CH",
        "Público",
        "Investimento",
        "Status"

    ]]

    for item in dados:

        investimento = (

            "Sem Investimento"

            if item["investimento"] == 0

            else f'R$ {item["investimento"]}'

        )

        tabela_dados.append([ 

            Paragraph(
                item["periodo"] or "",
                styles["BodyText"]
            ),

            Paragraph(
                item["descricao"] or "",
                styles["BodyText"]
            ),

            Paragraph(
                item["eixo"] or "",
                styles["BodyText"]
            ),

            Paragraph(
                f'{item["carga_horaria"]}h',
                styles["BodyText"]
            ),

            Paragraph(
                item["publico"] or "",
                styles["BodyText"]
            ),

            Paragraph(
                investimento,
                styles["BodyText"]
            ),

            Paragraph(
                item["status"] or "",
                styles["BodyText"]
            )

        ])

    tabela = Table(

        tabela_dados,

        repeatRows=1,

        colWidths=[

            70,   # período
            250,  # formação
            40,   # eixo
            40,   # CH
            150,  # público
            90,   # investimento
            70    # status

        ]

    )

    tabela.setStyle(TableStyle([

        ("BACKGROUND", (0, 0), (-1, 0), colors.black),

        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),

        ("GRID", (0, 0), (-1, -1), 1, colors.grey),

        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),

        ("FONTSIZE", (0, 0), (-1, -1), 9),

        ("BOTTOMPADDING", (0, 0), (-1, 0), 10),

        ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke),

        ("VALIGN", (0, 0), (-1, -1), "TOP"),

        ("ALIGN", (2, 0), (3, -1), "CENTER"),

        ("LEFTPADDING", (0, 0), (-1, -1), 6),

        ("RIGHTPADDING", (0, 0), (-1, -1), 6),

        ("TOPPADDING", (0, 0), (-1, -1), 4),

        ("BOTTOMPADDING", (0, 0), (-1, -1), 4)

    ]))

    elementos.append(tabela)

    elementos.append(
        Spacer(1, 20)
    )

    elementos.append(

        Paragraph(
            "<b>Descrição dos Eixos</b>",
            styles["Heading2"]
        )

    )

    elementos.append(
        Spacer(1, 10)
    )

    elementos.append(

        Paragraph(
            "I - Ambientação Institucional/Formação Inicial",
            styles["BodyText"]
        )

    )

    elementos.append(

        Paragraph(
            "II - Gestão do Trabalho/Saúde Mental e Bem Estar",
            styles["BodyText"]
        )

    )

    elementos.append(

        Paragraph(
            "III - Qualificação da Prática Socioeducativa Temas Transversais",
            styles["BodyText"]
        )

    )

    doc.build(elementos)

    return FileResponse(

        caminho,

        media_type="application/pdf",

        filename=f"cronograma_{ano}.pdf"

    )
