from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func

from database import SessionLocal
from models import Formacao
from schemas import FormacaoUpdate

router = APIRouter()


# =========================================
# DATABASE
# =========================================
def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


# =========================================
# LISTAR
# =========================================
@router.get("/api/formacoes")
def listar(
    busca: str = Query(None),
    pagina: int = 1,
    limite: int = 20,
    db: Session = Depends(get_db)
):

    query = db.query(Formacao)

    # =====================================
    # FILTRO
    # =====================================
    if busca:

        query = query.filter(
            Formacao.descricao.ilike(
                f"%{busca}%"
            )
        )

    total = query.count()

    dados = (
        query
        .order_by(
            Formacao.data_termino.desc()
        )
        .offset(
            (pagina - 1) * limite
        )
        .limit(limite)
        .all()
    )

    return {

        "dados": [

            {

                # =====================
                # BÁSICO
                # =====================
                "id":
                    f.id,

                "descricao":
                    f.descricao,

                "data_inicio":
                    f.data_inicio.strftime("%Y-%m-%d")
                    if f.data_inicio
                    else None,

                "data_termino":
                    f.data_termino.strftime("%Y-%m-%d")
                    if f.data_termino
                    else None,

                "periodo":
                    f.periodo,

                "ano_planejamento":
                    f.ano_planejamento,

                # =====================
                # FORMAÇÃO
                # =====================
                "carga_horaria":
                    f.carga_horaria,

                "modalidade":
                    str(f.modalidade)
                    if f.modalidade
                    else None,

                "eixo":
                    str(f.eixo)
                    if f.eixo
                    else None,

                "publico_alvo":
                    f.publico_alvo,

                "investimento":
                    float(f.investimento)
                    if f.investimento
                    else 0,

                # =====================
                # METAS
                # =====================
                "meta_participantes":
                    f.meta_participantes,
                
                # =====================
                # STATUS
                # =====================
                "status":
                    f.status,
                "ativo":
                    f.ativo
            }

            for f in dados
        ],

        "total":
            total,

        "total_paginas":
            (
                (total // limite)
                +
                (1 if total % limite else 0)
            )
    }


# =========================================
# CRIAR
# =========================================
@router.post("/api/formacao")
def criar(
    dados: dict,
    db: Session = Depends(get_db)
):

    existe = (
        db.query(Formacao)
        .filter(
            Formacao.descricao == dados["descricao"],
            Formacao.data_termino == dados["data_termino"]
        )
        .first()
    )

    if existe:

        return {
            "erro":
                "Formação já cadastrada"
        }

    try:

        nova = Formacao(

            descricao=
                dados.get("descricao"),

            data_inicio=
                dados.get("data_inicio"),

            data_termino=
                dados.get("data_termino"),

            periodo=
                dados.get("periodo"),

            ano_planejamento=
                dados.get("ano_planejamento"),

            carga_horaria=
                dados.get("carga_horaria"),

            modalidade=
                dados.get("modalidade"),

            eixo=
                dados.get("eixo"),

            publico_alvo=
                dados.get("publico_alvo"),

            investimento=
                dados.get("investimento"),

            meta_participantes=
                dados.get("meta_participantes", 0),            

            status=
                dados.get("status", "Planejada"),

            ativo=True
        )

        db.add(nova)

        db.commit()

        db.refresh(nova)

        return {
            "ok": True,
            "id": nova.id
        }

    except IntegrityError:

        db.rollback()

        return {
            "erro":
                "Erro ao salvar (possível duplicidade)"
        }

    except Exception as e:

        db.rollback()

        return {
            "erro": str(e)
        }


# =========================================
# ATUALIZAR
# =========================================
@router.put("/api/formacao/{id}")
def atualizar(
    id: int,
    dados: FormacaoUpdate,
    db: Session = Depends(get_db)
):

    f = db.get(Formacao, id)

    if not f:

        return {
            "erro":
                "Não encontrado"
        }

    try:

        for k, v in dados.dict(
            exclude_unset=True
        ).items():

            setattr(f, k, v)

        db.commit()

        db.refresh(f)

        return {
            "ok": True
        }

    except IntegrityError:

        db.rollback()

        return {
            "erro":
                "Duplicidade ao atualizar"
        }

    except Exception as e:

        db.rollback()

        return {
            "erro":
                str(e)
        }


# =========================================
# TOGGLE
# =========================================
@router.patch("/api/formacoes/toggle/{formacao_id}")
def toggle_formacao(
    formacao_id: int,
    db: Session = Depends(get_db)
):

    formacao = db.get(
        Formacao,
        formacao_id
    )

    if not formacao:

        raise HTTPException(
            status_code=404,
            detail="Formação não encontrada"
        )

    formacao.ativo = (
        not formacao.ativo
    )

    db.commit()

    return {

        "ok": True,

        "ativo":
            formacao.ativo
    }


# =========================================
# DESATIVAR
# =========================================
@router.delete("/api/formacoes/{formacao_id}")
def desativar_formacao(
    formacao_id: int,
    db: Session = Depends(get_db)
):

    formacao = db.get(
        Formacao,
        formacao_id
    )

    if not formacao:

        return {
            "erro":
                "Formação não encontrada"
        }

    formacao.ativo = False

    db.commit()

    return {

        "ok": True,

        "message":
            "Formação desativada"
    }


# =========================================
# ENUMS
# =========================================
@router.get("/api/enums")
def enums():

    return {

        "modalidade": [

            "presencial",
            "online",
            "hibrido"

        ],

        "eixo": [

            "Ambientação Institucional/Formação Inicial",

            "Gestão do Trabalho/Saúde Mental e Bem Estar",

            "Qualificação da Prática Socioeducativa Temas Transversais"
        ],

        "status": [

            "Planejada",

            "Em andamento",

            "Finalizada",

            "Cancelada",

            "Em construção"
        ]
    }
