from decimal import Decimal


def calcular_pagamento(
    frequencia,
    contrato,
    valor_hora,
    valor_va_fixo,
    valor_vt,
    dias_referencia,
    percentual_encargo
):

    valor_bolsa = (
        Decimal(str(frequencia.horas_realizadas))
        *
        valor_hora
    )


    if contrato.vale_alimentacao:

        valor_alimentacao = (
            valor_va_fixo
            /
            Decimal(dias_referencia)
        ) * Decimal(frequencia.dias)

    else:

        valor_alimentacao = Decimal("0.00")

    valor_alimentacao = valor_alimentacao.quantize(
        Decimal("0.01")
    )
    
    valor_transporte = (
        Decimal(frequencia.dias)
        *
        Decimal(contrato.quantidade_vale_transporte)
        *
        valor_vt
    )
    valor_transporte = valor_transporte.quantize(
        Decimal("0.01")
    )

    valor_total = (
        valor_bolsa
        +
        valor_alimentacao
        +
        valor_transporte
    )
    valor_total = valor_total.quantize(
        Decimal("0.01")
    )


    valor_encargo = (
        valor_total
        *
        percentual_encargo
    )


    return {

        "valor_hora_aplicado":
            valor_hora,

        "valor_vale_alimentacao":
            valor_alimentacao,

        "valor_vale_transporte":
            valor_transporte,

        "valor_total":
            valor_total,

        "valor_encargo":
            valor_encargo
    }
