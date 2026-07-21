from datetime import date
from decimal import Decimal

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    status
)
from sqlalchemy.orm import Session, joinedload

from database import get_db
from estagiario.enums import StatusPagamentoEstagioEnum
from estagiario.model_acompanhamento import (
    FrequenciaEstagio,
    PagamentoEstagio
)
from estagiario.model_estagiario import (
    BeneficioEstagiario,
    ClassificacaoEstagio,
    ContratoEstagio,
    Estagiario,
    ValorBolsaEstagio
)
from estagiario.routes.calcular_pagamento import calcular_pagamento
from schemas import PagamentoEstagioResponse

router = APIRouter(
    prefix="/api/pagamento_estagiario",
    tags=["Pagamento do Estágio"]
)

# ==========================================
# Funções Auxiliares (Helper Functions)
# ==========================================

def _obter_beneficio_vigente(db: Session, competencia: date) -> BeneficioEstagiario:
    beneficio = (
        db.query(BeneficioEstagiario)
        .filter(BeneficioEstagiario.data_inicio_vigencia <= competencia)
        .order_by(BeneficioEstagiario.data_inicio_vigencia.desc())
        .first()
    )
    if not beneficio:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não existe benefício vigente para a competência informada."
        )
    return beneficio


def _obter_valor_bolsa(db: Session, classificacao_id: int, competencia: date):
    return (
        db.query(ValorBolsaEstagio)
        .filter(
            ValorBolsaEstagio.classificacao_id == classificacao_id,
            ValorBolsaEstagio.data_inicio_vigencia <= competencia
        )
        .order_by(ValorBolsaEstagio.data_inicio_vigencia.desc())
        .first()
    )


def _buscar_frequencias(db: Session, competencia: date):
    return (
        db.query(FrequenciaEstagio)
        .join(ContratoEstagio, FrequenciaEstagio.contrato_id == ContratoEstagio.id)
        .join(ClassificacaoEstagio, ContratoEstagio.classificacao_id == ClassificacaoEstagio.id)
        .filter(
            FrequenciaEstagio.competencia == competencia,
            FrequenciaEstagio.status == StatusPagamentoEstagioEnum.ABERTA,
            ~ClassificacaoEstagio.descricao.ilike("%curricular%")
        )
        .options(
            joinedload(FrequenciaEstagio.contrato).joinedload(ContratoEstagio.estagiario),
            joinedload(FrequenciaEstagio.contrato).joinedload(ContratoEstagio.classificacao)
        )
        .all()
    )


def _montar_previa(db: Session, competencia: date, dias_referencia: int):
    beneficio = _obter_beneficio_vigente(db, competencia)
    frequencias = _buscar_frequencias(db, competencia)

    resultado = []

    for frequencia in frequencias:
        contrato = frequencia.contrato
        valor_bolsa = _obter_valor_bolsa(db, contrato.classificacao_id, competencia)

        if not valor_bolsa:
            continue

        valores = calcular_pagamento(
            frequencia,
            contrato,
            valor_bolsa.valor_hora,
            beneficio.valor_vale_alimentacao,
            beneficio.valor_vale_transporte,
            dias_referencia,
            Decimal("0.046")
        )

        resultado.append({
            "frequencia": frequencia,
            "contrato": contrato,
            "valor_hora": valor_bolsa.valor_hora,
            "valores": valores
        })

    return resultado


# ==========================================
# Rotas
# ==========================================

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
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não autenticado."
        )

    dados = _montar_previa(db, competencia, dias_referencia)
    quantidade = 0

    for item in dados:
        frequencia = item["frequencia"]

        existe = (
            db.query(PagamentoEstagio)
            .filter(PagamentoEstagio.frequencia_id == frequencia.id)
            .first()
        )

        if existe:
            continue

        pagamento = PagamentoEstagio(
            frequencia_id=frequencia.id,
            usuario_fechamento_id=usuario["id"],
            data_fechamento=date.today(),
            dias_referencia=dias_referencia,
            valor_hora_aplicado=item["valor_hora"],
            **item["valores"]
        )

        db.add(pagamento)
        frequencia.status = StatusPagamentoEstagioEnum.FECHADA
        quantidade += 1

    db.commit()

    return {
        "mensagem": "Folha fechada com sucesso.",
        "quantidade": quantidade
    }


@router.get("/", response_model=list[PagamentoEstagioResponse])
def listar_pagamentos(
    competencia: date,
    db: Session = Depends(get_db)
):
    pagamentos = (
        db.query(PagamentoEstagio)
        .join(FrequenciaEstagio, PagamentoEstagio.frequencia_id == FrequenciaEstagio.id)
        .join(ContratoEstagio, FrequenciaEstagio.contrato_id == ContratoEstagio.id)
        .join(Estagiario, ContratoEstagio.estagiario_id == Estagiario.id)
        .filter(FrequenciaEstagio.competencia == competencia)
        .options(
            joinedload(PagamentoEstagio.frequencia)
            .joinedload(FrequenciaEstagio.contrato)
            .joinedload(ContratoEstagio.estagiario)
        )
        .order_by(Estagiario.nome)
        .all()
    )

    return [
        {
            "id": pagamento.id,
            "frequencia_id": pagamento.frequencia_id,
            "numero_contrato": pagamento.frequencia.contrato.numero_contrato,
            "estagiario_nome": pagamento.frequencia.contrato.estagiario.nome,
            "competencia": pagamento.frequencia.competencia,
            "dias": pagamento.frequencia.dias,
            "horas_realizadas": pagamento.frequencia.horas_realizadas,
            "valor_hora_aplicado": pagamento.valor_hora_aplicado,
            "valor_vale_alimentacao": pagamento.valor_vale_alimentacao,
            "valor_vale_transporte": pagamento.valor_vale_transporte,
            "valor_total": pagamento.valor_total,
            "dias_referencia": pagamento.dias_referencia,
            "valor_encargo": pagamento.valor_encargo,
            "status": pagamento.frequencia.status,
            "data_fechamento": pagamento.data_fechamento,
            "usuario_fechamento_id": pagamento.usuario_fechamento_id
        }
        for pagamento in pagamentos
    ]


@router.get("/previa")
def previa_folha(
    competencia: date,
    dias_referencia: int,
    db: Session = Depends(get_db)
):
    dados = _montar_previa(db, competencia, dias_referencia)

    return [
        {
            "frequencia_id": item["frequencia"].id,
            "numero_contrato": item["contrato"].numero_contrato,
            "estagiario_nome": item["contrato"].estagiario.nome,
            "competencia": competencia,
            "dias": item["frequencia"].dias,
            "horas_realizadas": item["frequencia"].horas_realizadas,
            **item["valores"]
        }
        for item in dados
    ]


@router.delete("/{frequencia_id}", status_code=status.HTTP_200_OK)
def excluir_pagamento(
    frequencia_id: int,
    db: Session = Depends(get_db)
):
    pagamento = (
        db.query(PagamentoEstagio)
        .join(FrequenciaEstagio)
        .filter(PagamentoEstagio.frequencia_id == frequencia_id)
        .first()
    )

    if not pagamento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pagamento não encontrado."
        )

    # Reabre a frequência para permitir novo processamento
    pagamento.frequencia.status = StatusPagamentoEstagioEnum.ABERTA

    db.delete(pagamento)
    db.commit()

    return {"mensagem": "Pagamento excluído e frequência reaberta com sucesso."}
