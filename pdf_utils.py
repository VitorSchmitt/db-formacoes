import os

from reportlab.platypus import (
    Image,
    Table,
    TableStyle,
    Spacer,
    Paragraph
)

from reportlab.lib.units import cm
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import getSampleStyleSheet

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
    
