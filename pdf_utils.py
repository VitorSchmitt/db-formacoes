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

LOGO = "static/img/logo.png"
FASE = "static/img/fase.png"


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

def adicionar_cabecalho(elementos, styles, titulo):
    """
    Adiciona o cabeçalho padrão dos relatórios.
    """

    adicionar_logos(elementos)

    estilo_titulo = styles["Heading1"].clone("TituloRelatorio")
    estilo_titulo.alignment = TA_CENTER

    estilo_subtitulo = styles["Normal"].clone("SubtituloRelatorio")
    estilo_subtitulo.alignment = TA_CENTER

    elementos.append(
        Paragraph(
            titulo.upper(),
            estilo_titulo
        )
    )

    elementos.append(
        Paragraph(
            "CFP / NTEV",
            estilo_subtitulo
        )
    )

    elementos.append(
        Spacer(1, 0.5 * cm)
    )
