import os
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape

from reportlab.platypus import (
    SimpleDocTemplate,
    Image,
    Table,
    TableStyle,
    Spacer,
    Paragraph
)

from datetime import datetime
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import (
    getSampleStyleSheet,
    ParagraphStyle
)

LOGO = "static/img/logo.png"
FASE = "static/img/fase.png"
NOME_SETOR = "CFP / NTEV"

def adicionar_logos(elementos):
    """
    Adiciona as logos institucionais ao PDF.

    Parameters
    ----------
    elementos : list
        Lista de elementos do ReportLab.
    """

    logo_esquerda = ""
    logo_direita = ""

    if os.path.exists(LOGO):
        logo_esquerda = Image(
            LOGO,
            width=5 * cm,
            height=2.5 * cm
        )

    if os.path.exists(FASE):
        logo_direita = Image(
            FASE,
            width=2.5 * cm,
            height=2.5 * cm
        )

    tabela = Table(
        [[logo_esquerda, logo_direita]],
        colWidths=[9 * cm, 9 * cm]
    )

    tabela.setStyle(
        TableStyle([
            ("ALIGN", (0, 0), (0, 0), "LEFT"),
            ("ALIGN", (1, 0), (1, 0), "RIGHT"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ])
    )

    elementos.append(tabela)
    elementos.append(Spacer(1, 12))

def adicionar_cabecalho(elementos, titulo):
    """
    Adiciona o cabeçalho padrão dos relatórios.
    """

    styles = getSampleStyleSheet()

    adicionar_logos(elementos)

    estilo_titulo = styles["Heading1"]
    estilo_titulo.alignment = TA_CENTER

    estilo_subtitulo = styles["Normal"]
    estilo_subtitulo.alignment = TA_CENTER

    elementos.append(
        Paragraph(
            titulo.upper(),
            estilo_titulo
        )
    )

    elementos.append(
        Paragraph(
            NOME_SETOR,
            estilo_subtitulo
        )
    )

    elementos.append(
        Spacer(1, 0.5 * cm)
    )

def aplicar_estilo_tabela(tabela, estilos_extras=None):

    estilos = [

        ("BACKGROUND", (0, 0), (-1, 0), colors.black),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 1, colors.grey),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
        ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]

    if estilos_extras:
        estilos.extend(estilos_extras)

    tabela.setStyle(TableStyle(estilos))



def criar_documento_pdf(
        arquivo,
        orientacao="portrait"
    ):
        """
        Cria um documento PDF com margens padrão e orientação configurável.
        """
    
        paginas = A4
    
        if orientacao == "landscape":
            paginas = landscape(A4)
    
        return SimpleDocTemplate(
            arquivo,
            pagesize=paginas,
            rightMargin=1.5 * cm,
            leftMargin=1.5 * cm,
            topMargin=1.5 * cm,
            bottomMargin=1 * cm
        )



def adicionar_data_emissao(elementos, estilo_direita):
    """
    Adiciona a data de emissão do relatório.
    """

    meses = {
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

    hoje = datetime.now()

    data_emissao = (
        f"{hoje.day} de "
        f"{meses[hoje.month]} de "
        f"{hoje.year}"
    )

    tabela = Table(
        [[
            Paragraph(
                f"Porto Alegre, {data_emissao}",
                estilo_direita
            )
        ]],
        colWidths=[17 * cm]
    )

    tabela.setStyle(
        TableStyle([
            ("ALIGN", (0, 0), (0, 0), "RIGHT")
        ])
    )

    elementos.append(Spacer(1, 30))
    elementos.append(tabela)

def obter_estilo_tabela():
    """
    Retorna o estilo utilizado nas células das tabelas.
    """

    styles = getSampleStyleSheet()

    return ParagraphStyle(
        "Tabela",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=10,
        leading=10,
    )
