from decimal import Decimal, ROUND_HALF_UP


def calcular_pagamento(
    frequencia,
    contrato,
    valor_hora: Decimal,
    valor_va_fixo: Decimal,
    valor_vt: Decimal,
    dias_referencia: int,
    percentual_encargo: Decimal
) -> dict:
    """
    Calcula os valores de bolsa, VA, VT e encargos para a folha de estágio.
    """
    
    # -------------------------------------------------------------------------
    # 1. Cálculo da Bolsa Auxílio
    # -------------------------------------------------------------------------
    horas = Decimal(str(frequencia.horas_realizadas or 0))
    valor_bolsa = (horas * Decimal(str(valor_hora))).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )

    # -------------------------------------------------------------------------
    # 2. Cálculo do Vale Alimentação
    # -------------------------------------------------------------------------
    if contrato.vale_alimentacao and dias_referencia > 0:
        dias_frequencia = Decimal(str(frequencia.dias or 0))
        dias_ref = Decimal(str(dias_referencia))
        
        valor_alimentacao = (
            Decimal(str(valor_va_fixo)) / dias_ref
        ) * dias_frequencia
    else:
        valor_alimentacao = Decimal("0.00")

    valor_alimentacao = valor_alimentacao.quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )

    # -------------------------------------------------------------------------
    # 3. Cálculo do Vale Transporte
    # -------------------------------------------------------------------------
    qtd_vt = Decimal(str(getattr(contrato, "quantidade_vale_transporte", 0) or 0))
    dias_frequencia = Decimal(str(frequencia.dias or 0))

    valor_transporte = (
        dias_frequencia * qtd_vt * Decimal(str(valor_vt))
    ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    # -------------------------------------------------------------------------
    # 4. Totais e Encargos
    # -------------------------------------------------------------------------
    valor_total = (valor_bolsa + valor_alimentacao + valor_transporte).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )

    valor_encargo = (valor_total * Decimal(str(percentual_encargo))).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )

    return {
        "valor_hora_aplicado": Decimal(str(valor_hora)),
        "valor_vale_alimentacao": valor_alimentacao,
        "valor_vale_transporte": valor_transporte,
        "valor_total": valor_total,
        "valor_encargo": valor_encargo
    }
