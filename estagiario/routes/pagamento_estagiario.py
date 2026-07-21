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

    usuario_id = usuario.get("id")
    beneficio = _obter_beneficio_vigente(db, competencia)

    # Buscar frequências abertas (ignorando estágio curricular)
    frequencias = (
        db.query(FrequenciaEstagio)
        .join(ContratoEstagio, FrequenciaEstagio.contrato_id == ContratoEstagio.id)
        .join(ClassificacaoEstagio, ContratoEstagio.classificacao_id == ClassificacaoEstagio.id)
        .filter(
            FrequenciaEstagio.competencia == competencia,
            FrequenciaEstagio.status == StatusPagamentoEstagioEnum.ABERTA,
            ~ClassificacaoEstagio.descricao.ilike("%curricular%")
        )
        .options(
            joinedload(FrequenciaEstagio.contrato)
            .joinedload(ContratoEstagio.classificacao)
        )
        .all()
    )

    if not frequencias:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nenhuma frequência disponível para fechamento."
        )

    quantidade = 0

    for frequencia in frequencias:
        # Evita duplicidade de processamento de pagamento
        existe = (
            db.query(PagamentoEstagio)
            .filter(PagamentoEstagio.frequencia_id == frequencia.id)
            .first()
        )
        if existe:
            continue

        contrato = frequencia.contrato

        valor_bolsa = (
            db.query(ValorBolsaEstagio)
            .filter(
                ValorBolsaEstagio.classificacao_id == contrato.classificacao_id,
                ValorBolsaEstagio.data_inicio_vigencia <= competencia
            )
            .order_by(ValorBolsaEstagio.data_inicio_vigencia.desc())
            .first()
        )

        if not valor_bolsa:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Sem valor de bolsa cadastrado para o contrato {contrato.numero_contrato}."
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
    beneficio = _obter_beneficio_vigente(db, competencia)

    frequencias = (
        db.query(FrequenciaEstagio)
        .join(ContratoEstagio, FrequenciaEstagio.contrato_id == ContratoEstagio.id)
        .join(ClassificacaoEstagio, ContratoEstagio.classificacao_id == ClassificacaoEstagio.id)
        .filter(
            FrequenciaEstagio.competencia == competencia,
            FrequenciaEstagio.status == StatusPagamentoEstagioEnum.ABERTA,
            ContratoEstagio.data_inicio <= competencia,
            ContratoEstagio.data_fim >= competencia,
            ~ClassificacaoEstagio.descricao.ilike("%curricular%")
        )
        .options(
            joinedload(FrequenciaEstagio.contrato)
            .joinedload(ContratoEstagio.estagiario),
            joinedload(FrequenciaEstagio.contrato)
            .joinedload(ContratoEstagio.classificacao)
        )
        .all()
    )

    if not frequencias:
        return []

    resultado = []

    for frequencia in frequencias:
        contrato = frequencia.contrato

        valor_bolsa = (
            db.query(ValorBolsaEstagio)
            .filter(
                ValorBolsaEstagio.classificacao_id == contrato.classificacao_id,
                ValorBolsaEstagio.data_inicio_vigencia <= competencia
            )
            .order_by(ValorBolsaEstagio.data_inicio_vigencia.desc())
            .first()
        )

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
            "frequencia_id": frequencia.id,
            "numero_contrato": contrato.numero_contrato,
            "estagiario_nome": contrato.estagiario.nome,
            "competencia": competencia,
            "dias": frequencia.dias,
            "horas_realizadas": frequencia.horas_realizadas,
            **valores
        })

    return resultado
// =====================================================
// CARREGAR PRÉVIA DA FOLHA
// =====================================================
function carregarPrevia() {
    const competencia = document.getElementById("competencia").value;
    const dias = document.getElementById("dias_referencia").value;

    if (!competencia) {
        alert("Informe a competência.");
        return;
    }

    fetch(`${urlPagamento}/previa?competencia=${competencia}-01&dias_referencia=${dias}`)
        .then(r => {
            if (!r.ok) {
                throw new Error("Erro ao carregar prévia da folha.");
            }
            return r.json();
        })
        .then(dados => {
            let html = "";
            let totalBolsa = 0;
            let totalEncargo = 0;
            let totalFolha = 0;
            let quantidade = dados.length;

            if (quantidade === 0) {
                html = `
                    <tr>
                        <td colspan="11" class="text-center text-muted">
                            Nenhuma prévia encontrada para a competência selecionada.
                        </td>
                    </tr>
                `;
                document.getElementById("btnFechar").disabled = true;
            } else {
                dados.forEach(item => {
                    const va = Number(item.valor_vale_alimentacao || 0);
                    const vt = Number(item.valor_vale_transporte || 0);
                    const encargo = Number(item.valor_encargo || 0);
                    const total = Number(item.valor_total || 0);

                    totalBolsa += (total - encargo - va - vt);
                    totalEncargo += encargo;
                    totalFolha += total;

                    const badge = `<span class="badge bg-warning text-dark">PRÉVIA</span>`;

                    html += `
                        <tr>
                            <td>${item.numero_contrato ?? "-"}</td>
                            <td>${item.estagiario_nome ?? "-"}</td>
                            <td>${item.competencia}</td>
                            <td>${item.dias ?? "-"}</td>
                            <td>${Number(item.horas_realizadas || 0).toFixed(2)}</td>
                            <td>R$ ${formatarMoeda(item.valor_hora_aplicado)}</td>
                            <td>R$ ${formatarMoeda(va)}</td>
                            <td>R$ ${formatarMoeda(vt)}</td>
                            <td>R$ ${formatarMoeda(encargo)}</td>
                            <td><strong>R$ ${formatarMoeda(total)}</strong></td>
                            <td>${badge}</td>
                        </tr>
                    `;
                });

                // Habilita o botão de fechar folha caso existam registros na prévia
                document.getElementById("btnFechar").disabled = false;
            }

            document.getElementById("lista").innerHTML = html;
            document.getElementById("totalEstagiarios").innerHTML = quantidade;
            document.getElementById("totalBolsa").innerHTML = "R$ " + formatarMoeda(totalBolsa);
            document.getElementById("totalEncargo").innerHTML = "R$ " + formatarMoeda(totalEncargo);
            document.getElementById("totalFolha").innerHTML = "R$ " + formatarMoeda(totalFolha);
        })
        .catch(err => {
            console.error(err);
            alert(err.message);
        });
}

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

    if pagamento.frequencia.status == StatusPagamentoEstagioEnum.FECHADA:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A folha já foi encerrada e não pode ser excluída."
        )

    db.delete(pagamento)
    db.commit()

    return {"mensagem": "Pagamento excluído com sucesso."}
