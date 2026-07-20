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
