from io import BytesIO
from decimal import Decimal
from datetime import date
from reportlab.lib.units import cm
from fastapi.responses import StreamingResponse
from reportlab.lib import colors

from reportlab.platypus import (
    Table,
    TableStyle,
    Paragraph,
    Spacer
)

from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_RIGHT

from pdf_utils import (
    criar_documento_pdf,
    adicionar_cabecalho,
    aplicar_estilo_tabela,
    adicionar_data_emissao,
    obter_estilo_tabela
)


# ==========================================================
# FORMATAÇÕES
# ==========================================================

def moeda(valor):

    if valor is None:
        valor = Decimal("0.00")

    texto = f"{valor:,.2f}"

    texto = (
        texto
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )

    return f"R$ {texto}"


def competencia_extenso(comp: date):

    meses = {
        1: "Janeiro",
        2: "Fevereiro",
        3: "Março",
        4: "Abril",
        5: "Maio",
        6: "Junho",
        7: "Julho",
        8: "Agosto",
        9: "Setembro",
        10: "Outubro",
        11: "Novembro",
        12: "Dezembro"
    }

    return f"{meses[comp.month]} de {comp.year}"


# ==========================================================
# TÍTULO ESPECÍFICO
# ==========================================================

def adicionar_competencia(elementos, competencia):

    styles = getSampleStyleSheet()

    elementos.append(
        Paragraph(
            f"<b>Competência:</b> {competencia_extenso(competencia)}",
            styles["Normal"]
        )
    )

    elementos.append(Spacer(1, 0.4 * cm))



# ==========================================================
# TABELA DA FOLHA
# ==========================================================

def montar_tabela_pagamentos(pagamentos):

    estilo = obter_estilo_tabela()

    dados = [[
        Paragraph("<b>Contrato</b>", estilo),
        Paragraph("<b>Estagiário</b>", estilo),
        Paragraph("<b>Dias</b>", estilo),
        Paragraph("<b>Horas</b>", estilo),
        Paragraph("<b>Vlr Hora</b>", estilo),
        Paragraph("<b>Bolsa</b>", estilo),
        Paragraph("<b>V.A.</b>", estilo),
        Paragraph("<b>V.T.</b>", estilo),
        Paragraph("<b>Encargos</b>", estilo),
        Paragraph("<b>Total</b>", estilo)
    ]]

    resumo = {
        "quantidade": 0,
        "bolsa": Decimal("0.00"),
        "vale_alimentacao": Decimal("0.00"),
        "vale_transporte": Decimal("0.00"),
        "encargos": Decimal("0.00"),
        "total": Decimal("0.00")
    }

    for pagamento in pagamentos:

        frequencia = pagamento.frequencia
        contrato = frequencia.contrato
        estagiario = contrato.estagiario

        bolsa = (
            Decimal(frequencia.horas_realizadas)
            * Decimal(pagamento.valor_hora_aplicado)
        )

        resumo["quantidade"] += 1
        resumo["bolsa"] += bolsa
        resumo["vale_alimentacao"] += pagamento.valor_vale_alimentacao
        resumo["vale_transporte"] += pagamento.valor_vale_transporte
        resumo["encargos"] += pagamento.valor_encargo
        resumo["total"] += pagamento.valor_total

        dados.append([

            Paragraph(
                contrato.numero_contrato,
                estilo
            ),

            Paragraph(
                estagiario.nome,
                estilo
            ),

            Paragraph(
                str(frequencia.dias),
                estilo
            ),

            Paragraph(
                f"{Decimal(frequencia.horas_realizadas):.2f}",
                estilo
            ),

            Paragraph(
                moeda(pagamento.valor_hora_aplicado),
                estilo
            ),

            Paragraph(
                moeda(bolsa),
                estilo
            ),

            Paragraph(
                moeda(
                    pagamento.valor_vale_alimentacao
                ),
                estilo
            ),

            Paragraph(
                moeda(
                    pagamento.valor_vale_transporte
                ),
                estilo
            ),

            Paragraph(
                moeda(
                    pagamento.valor_encargo
                ),
                estilo
            ),

            Paragraph(
                moeda(
                    pagamento.valor_total
                ),
                estilo
            )

        ])

    tabela = Table(
        dados,
        repeatRows=1,
        colWidths=[
            2.6 * cm,
            6.2 * cm,
            1.3 * cm,
            1.8 * cm,
            2.2 * cm,
            2.3 * cm,
            2.2 * cm,
            2.2 * cm,
            2.3 * cm,
            2.5 * cm
        ]
    )

    aplicar_estilo_tabela(tabela)

    return tabela, resumo


# ==========================================================
# RESUMO FINANCEIRO
# ==========================================================


def montar_resumo(resumo):

    estilo = obter_estilo_tabela()

    dados = [

        [
            Paragraph("<b>RESUMO FINANCEIRO</b>", estilo),
            ""
        ],

        [
            Paragraph("Quantidade de Estagiários", estilo),
            Paragraph(
                str(resumo["quantidade"]),
                estilo
            )
        ],

        [
            Paragraph("Total da Bolsa", estilo),
            Paragraph(
                moeda(resumo["bolsa"]),
                estilo
            )
        ],

        [
            Paragraph("Vale Alimentação", estilo),
            Paragraph(
                moeda(
                    resumo["vale_alimentacao"]
                ),
                estilo
            )
        ],

        [
            Paragraph("Vale Transporte", estilo),
            Paragraph(
                moeda(
                    resumo["vale_transporte"]
                ),
                estilo
            )
        ],

        [
            Paragraph("Encargos", estilo),
            Paragraph(
                moeda(
                    resumo["encargos"]
                ),
                estilo
            )
        ],

        [
            Paragraph(
                "<b>TOTAL DA FOLHA</b>",
                estilo
            ),
            Paragraph(
                f"<b>{moeda(resumo['total'])}</b>",
                estilo
            )
        ]

    ]

    tabela = Table(
        dados,
        colWidths=[
            7 * cm,
            4 * cm
        ]
    )

    aplicar_estilo_tabela(
        tabela,
        estilos_extras=[

            ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),

            ("BACKGROUND", (0, -1), (-1, -1), colors.lightgrey),

            ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),

            ("ALIGN", (1, 0), (1, -1), "RIGHT")

        ]
    )

    return tabela
    """

    pass


# ==========================================================
# PDF
# ==========================================================

def gerar_pdf_folha(
    pagamentos,
    competencia
):

    buffer = BytesIO()

    documento = criar_documento_pdf(
        buffer,
        orientacao="landscape"
    )

    elementos = []

    adicionar_cabecalho(
        elementos,
        "Folha de Pagamento de Estagiários"
    )

    adicionar_competencia(
        elementos,
        competencia
    )

    tabela, resumo = montar_tabela_pagamentos(
        pagamentos
    )

    elementos.append(tabela)

    elementos.append(
        Spacer(1, 0.5 * cm)
    )

    resumo = montar_resumo(resumo)

    wrapper = Table(
        [["", resumo]],
        colWidths=[14 * cm, 11 * cm]
    )
    
    wrapper.setStyle(
        TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("ALIGN", (1, 0), (1, 0), "RIGHT")
        ])
    )
    
    elementos.append(wrapper)

    styles = getSampleStyleSheet()

    estilo_direita = styles["Normal"]
    estilo_direita.alignment = TA_RIGHT

    adicionar_data_emissao(
        elementos,
        estilo_direita
    )

    documento.build(elementos)

    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition":
                f'inline; filename="folha_{competencia.strftime("%Y_%m")}.pdf"'
        }
    )
