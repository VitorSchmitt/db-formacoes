from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session, joinedload

from database import get_db

from estagiario.model_acompanhamento import (
    AvaliacaoSupervisor,
    FrequenciaEstagio
)

from estagiario.model_estagiario import ContratoEstagio

from schemas import (
    AvaliacaoSupervisorCreate,
    AvaliacaoSupervisorUpdate
)


router = APIRouter(
    prefix="/api/avaliacao_estagiario",
    tags=["Avaliação do Supervisor"]
)


# =====================================================
# LISTAR
# =====================================================

@router.get("/")
def listar(
    request: Request,
    db: Session = Depends(get_db)
):

    usuario = request.session.get("user")

    if not usuario:
        raise HTTPException(
            status_code=401,
            detail="Usuário não autenticado."
        )


    perfil = usuario.get("perfil")
    matricula = usuario.get("matricula")    

    query = (
        db.query(AvaliacaoSupervisor)
        .join(
            FrequenciaEstagio,
            AvaliacaoSupervisor.frequencia_id ==
            FrequenciaEstagio.id
        )
        .join(
            ContratoEstagio,
            FrequenciaEstagio.contrato_id ==
            ContratoEstagio.id
        )
        .options(
            joinedload(
                AvaliacaoSupervisor.frequencia
            )
            .joinedload(
                FrequenciaEstagio.contrato
            )
            .joinedload(
                ContratoEstagio.estagiario
            )
        )
    )


    if perfil == "operadorIV":

        query = query.filter(
           ContratoEstagio.supervisor_matricula ==matricula
        )


    avaliacoes = (
        query
        .order_by(
            FrequenciaEstagio.competencia.desc()
        )
        .all()
    )


    retorno = []


    for av in avaliacoes:

        frequencia = av.frequencia
        contrato = frequencia.contrato
        estagiario = contrato.estagiario


        retorno.append({

            "id": av.id,

            "frequencia_id":
                av.frequencia_id,

            "contrato_id":
                contrato.id,

            "numero_contrato":
                contrato.numero_contrato,

            "estagiario_nome":
                estagiario.nome,

            "competencia":
                frequencia.competencia.strftime("%m/%Y"),

            "data_avaliacao":
                av.data_avaliacao.isoformat(),

            "avaliacao":
                av.avaliacao,

            "parecer":
                av.parecer

        })


    return retorno



# =====================================================
# BUSCAR POR ID
# =====================================================



# =====================================================
# INSERIR
# =====================================================

@router.post(
    "/",
    status_code=status.HTTP_201_CREATED
)
def inserir(
    dados: AvaliacaoSupervisorCreate,
    request: Request,
    db: Session = Depends(get_db)
):

    usuario = request.session.get("user")


    if not usuario:

        raise HTTPException(
            status_code=401,
            detail="Usuário não autenticado."
        )


    perfil = usuario.get("perfil")
    matricula = usuario.get("matricula")


    # -------------------------------------
    # Busca frequência
    # -------------------------------------

    frequencia = (
        db.query(FrequenciaEstagio)
        .options(
            joinedload(
                FrequenciaEstagio.contrato
            )
        )
        .filter(
            FrequenciaEstagio.id ==
            dados.frequencia_id
        )
        .first()
    )


    if not frequencia:

        raise HTTPException(
            status_code=400,
            detail="Frequência não encontrada."
        )


    contrato = frequencia.contrato


    # -------------------------------------
    # Permissão supervisor
    # -------------------------------------

    if perfil == "operadorIV":

        if int(contrato.supervisor_matricula) != int(matricula):

            raise HTTPException(
                status_code=403,
                detail="Você não possui permissão para avaliar este estagiário."
            )


    # -------------------------------------
    # Verifica duplicidade
    # -------------------------------------

    existe = (
        db.query(AvaliacaoSupervisor)
        .filter(
            AvaliacaoSupervisor.frequencia_id ==
            dados.frequencia_id
        )
        .first()
    )


    if existe:

        raise HTTPException(
            status_code=400,
            detail="Esta frequência já possui avaliação."
        )


    nova = AvaliacaoSupervisor(

        frequencia_id=
            dados.frequencia_id,

        data_avaliacao=
            dados.data_avaliacao,

        avaliacao=
            dados.avaliacao,

        parecer=
            dados.parecer
    )


    db.add(nova)

    db.commit()

    db.refresh(nova)


    return {
        "mensagem":
        "Avaliação registrada com sucesso."
    }



# =====================================================
# ALTERAR
# =====================================================

@router.put("/{id}")
def alterar(
    id: int,
    dados: AvaliacaoSupervisorUpdate,
    db: Session = Depends(get_db)
):

    avaliacao = (
        db.query(AvaliacaoSupervisor)
        .filter(
            AvaliacaoSupervisor.id == id
        )
        .first()
    )


    if not avaliacao:

        raise HTTPException(
            status_code=404,
            detail="Avaliação não encontrada."
        )


    dados_atualizar = (
        dados.model_dump(
            exclude_unset=True
        )
    )


    # não permite trocar frequência
    if "frequencia_id" in dados_atualizar:

        if dados_atualizar["frequencia_id"] != avaliacao.frequencia_id:

            raise HTTPException(
                status_code=400,
                detail="Não é permitido alterar a frequência vinculada."
            )


    for chave, valor in dados_atualizar.items():

        setattr(
            avaliacao,
            chave,
            valor
        )


    db.commit()

    db.refresh(avaliacao)


    return {
        "mensagem":
        "Avaliação atualizada com sucesso."
    }



# =====================================================
# EXCLUIR
# =====================================================

@router.delete("/{id}")
def excluir(
    id: int,
    db: Session = Depends(get_db)
):

    avaliacao = (
        db.query(AvaliacaoSupervisor)
        .filter(
            AvaliacaoSupervisor.id == id
        )
        .first()
    )


    if not avaliacao:

        raise HTTPException(
            status_code=404,
            detail="Avaliação não encontrada."
        )


    db.delete(avaliacao)

    db.commit()


    return {
        "mensagem":
        "Avaliação excluída com sucesso."
    }
