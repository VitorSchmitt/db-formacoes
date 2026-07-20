from datetime import date
from decimal import Decimal

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    status
)

from sqlalchemy.orm import (
    Session,
    joinedload
)

from database import get_db

from estagiario.model_acompanhamento import (
    FrequenciaEstagio,
    PagamentoEstagio
)

from estagiario.model_estagiario import (
    ContratoEstagio,
    ClassificacaoEstagio,
    BeneficioEstagiario,
    Estagiario,
    ValorBolsaEstagio
)
from estagiario.routes.calcular_pagamento import calcular_pagamento

from enums import StatusFolhaEnum
from schemas import PagamentoEstagioResponse


router = APIRouter(
    prefix="/api/pagamento",
    tags=["Pagamento do Estágio"]
)

@router.post("/fechar")
def fechar_folha(
    competencia: date,
    dias_referencia: int,
    request: Request,
    db: Session = Depends(get_db)
):

    usuario = request.session.get("user")

    if not usuario:
        raise HTTPException(
            status_code=401,
            detail="Usuário não autenticado."
        )


    usuario_id = usuario.get("id")


    # ==========================================
    # Benefícios vigentes
    # ==========================================

    beneficio = (
        db.query(BeneficioEstagiario)
        .filter(
            BeneficioEstagiario.data_inicio_vigencia <= competencia
        )
        .order_by(
            BeneficioEstagiario.data_inicio_vigencia.desc()
        )
        .first()
    )


    if not beneficio:
        raise HTTPException(
            400,
            "Não existe benefício vigente."
        )


    # ==========================================
    # Frequências que entram na folha
    # ==========================================

    frequencias = (
        db.query(FrequenciaEstagio)
        .join(
            ContratoEstagio,
            FrequenciaEstagio.contrato_id ==
            ContratoEstagio.id
        )
        .join(
            ClassificacaoEstagio,
            ContratoEstagio.classificacao_id ==
            ClassificacaoEstagio.id
        )
        .filter(
            FrequenciaEstagio.competencia == competencia,

            FrequenciaEstagio.status ==
            StatusFolhaEnum.ABERTA,

            # Não paga estágio curricular
            ~ClassificacaoEstagio.descricao.ilike(
                "%curricular%"
            )
        )
        .options(
            joinedload(
                FrequenciaEstagio.contrato
            )
            .joinedload(
                ContratoEstagio.classificacao
            )
        )
        .all()
    )


    if not frequencias:
        raise HTTPException(
            400,
            "Nenhuma frequência disponível para fechamento."
        )


    quantidade = 0


    for frequencia in frequencias:


        # --------------------------------------
        # Evita duplicidade
        # --------------------------------------

        existe = (
            db.query(PagamentoEstagio)
            .filter(
                PagamentoEstagio.frequencia_id ==
                frequencia.id
            )
            .first()
        )


        if existe:
            continue



        contrato = frequencia.contrato


        # --------------------------------------
        # Valor hora vigente
        # --------------------------------------

        valor_bolsa = (
            db.query(ValorBolsaEstagio)
            .filter(
                ValorBolsaEstagio.classificacao_id ==
                contrato.classificacao_id,

                ValorBolsaEstagio.data_inicio_vigencia
                <= competencia
            )
            .order_by(
                ValorBolsaEstagio.data_inicio_vigencia.desc()
            )
            .first()
        )


        if not valor_bolsa:
            raise HTTPException(
                400,
                f"Sem valor de bolsa para {contrato.numero_contrato}"
            )


        valores = calcular_pagamento(
            frequencia,
            contrato,
            valor_bolsa.valor_hora,
            beneficio.valor_vale_alimentacao,
            beneficio.valor_vale_transporte,
            dias_referencia,
            Decimal("0.046")
        )


        pagamento = PagamentoEstagio(

            frequencia_id=frequencia.id,

            usuario_fechamento_id=usuario_id,

            data_fechamento=date.today(),

            dias_referencia=dias_referencia,

            **valores
        )


        db.add(pagamento)


        frequencia.status = StatusFolhaEnum.FECHADA


        quantidade += 1


    db.commit()


    return {

        "mensagem":
            "Folha fechada com sucesso.",

        "quantidade":
            quantidade
    }
    
@router.get(
    "/",
    response_model=list[PagamentoEstagioResponse]
)
def listar_pagamentos(
    competencia: date,
    db: Session = Depends(get_db)
):

    pagamentos = (
        db.query(PagamentoEstagio)
        .join(
            FrequenciaEstagio,
            PagamentoEstagio.frequencia_id == FrequenciaEstagio.id
        )
        .join(
            ContratoEstagio,
            FrequenciaEstagio.contrato_id == ContratoEstagio.id
        )
        .join(
            Estagiario,
            ContratoEstagio.estagiario_id == Estagiario.id
        )
        .filter(
            FrequenciaEstagio.competencia == competencia
        )
        .order_by(
            Estagiario.nome
        )
        .all()
    )


    return [

        {
            "id": pagamento.id,

            "frequencia_id":
                pagamento.frequencia_id,

            "numero_contrato":
                pagamento.frequencia.contrato.numero_contrato,

            "estagiario_nome":
                pagamento.frequencia.contrato.estagiario.nome,

            "competencia":
                pagamento.frequencia.competencia,

            "dias":
                pagamento.frequencia.dias,

            "horas_realizadas":
                pagamento.frequencia.horas_realizadas,

            "valor_hora_aplicado":
                pagamento.valor_hora_aplicado,

            "valor_vale_alimentacao":
                pagamento.valor_vale_alimentacao,

            "valor_vale_transporte":
                pagamento.valor_vale_transporte,

            "valor_total":
                pagamento.valor_total,

            "dias_referencia":
                pagamento.dias_referencia,

            "valor_encargo":
                pagamento.valor_encargo,

            "status":
                pagamento.frequencia.status,

            "data_fechamento":
                pagamento.data_fechamento,

            "usuario_fechamento_id":
                pagamento.usuario_fechamento_id
        }

        for pagamento in pagamentos

    ]
@router.delete("/{frequencia_id}")
def excluir_pagamento(
    frequencia_id: int,
    db: Session = Depends(get_db)
):

    pagamento = (
        db.query(PagamentoEstagio)
        .join(FrequenciaEstagio)
        .filter(
            PagamentoEstagio.frequencia_id == frequencia_id
        )
        .first()
    )

    if not pagamento:
        raise HTTPException(
            status_code=404,
            detail="Pagamento não encontrado."
        )

    # Não permite excluir pagamento de folha encerrada
    if pagamento.frequencia.status == StatusFolhaEnum.FECHADA:
        raise HTTPException(
            status_code=400,
            detail="A folha já foi encerrada."
        )

    db.delete(pagamento)
    db.commit()

    return {
        "mensagem": "Pagamento excluído."
    }
