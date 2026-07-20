from datetime import date

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
    BeneficioEstagiario
)

from models import Usuario

from schemas import PagamentoEstagioResponse

router = APIRouter(
    prefix="/api/pagamento",
    tags=["Pagamento do Estágio"]
)

@router.get("/")
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

            "frequencia_id": pagamento.frequencia_id,

            "numero_contrato":
                pagamento.frequencia.contrato.numero_contrato,

            "estagiario_nome":
                pagamento.frequencia.contrato.estagiario.nome,

            "competencia":
                pagamento.frequencia.competencia.strftime("%m/%Y"),

            "dias":
                pagamento.frequencia.dias,

            "horas_realizadas":
                float(pagamento.frequencia.horas_realizadas),

            "valor_hora_aplicado":
                float(pagamento.valor_hora_aplicado),

            "valor_vale_alimentacao":
                float(pagamento.valor_vale_alimentacao),

            "valor_vale_transporte":
                float(pagamento.valor_vale_transporte),

            "valor_total":
                float(pagamento.valor_total),

            "fechado":
                pagamento.fechado,

            "data_fechamento":
                pagamento.data_fechamento,

            "usuario_fechamento_id":
                pagamento.usuario_fechamento_id

        }

        for pagamento in pagamentos

    ]
