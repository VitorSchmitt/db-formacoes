from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

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

        "dados":[

            {

                "id":f.id,

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

                "carga_horaria":
                    f.carga_horaria,

                "modalidade":
                    str(f.modalidade)
                    if f.modalidade
                    else None,

                "publico_alvo":
                    f.publico_alvo,

                "investimento":
                    float(f.investimento)
                    if f.investimento
                    else 0,

                "meta_participantes":
                    f.meta_participantes,

                "status":
                    str(f.status),

                "plano_anual_id":
                    f.plano_anual_id,

                "ativo":
                    f.ativo

            }

            for f in dados

        ],

        "total":total,

        "total_paginas":

        (

            total // limite

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

    campos_obrigatorios=[

        "descricao",
        "data_inicio",
        "data_termino",
        "carga_horaria",
        "modalidade",
        "periodo",
        "publico_alvo",
        "meta_participantes",
        "investimento",
        "status",
        "plano_anual_id"

    ]

    faltando=[

        campo

        for campo in campos_obrigatorios

        if not dados.get(campo)

    ]

    if faltando:

        return {

            "erro":
            f"Campos obrigatórios: {', '.join(faltando)}"

        }


    existe=(

        db.query(Formacao)

        .filter(

            Formacao.descricao
            ==
            dados.get("descricao"),

            Formacao.data_termino
            ==
            dados.get("data_termino")

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

            carga_horaria=
                dados.get("carga_horaria"),

            modalidade=
                dados.get("modalidade"),

            publico_alvo=
                dados.get("publico_alvo"),

            investimento=
                dados.get("investimento"),

            meta_participantes=
                dados.get("meta_participantes"),

            status=
                dados.get("status"),

            plano_anual_id=
                dados.get("plano_anual_id"),

            ativo=True

        )

        db.add(nova)

        db.commit()

        db.refresh(nova)

        return {

            "ok":True,
            "id":nova.id

        }

    except IntegrityError:

        db.rollback()

        return {

            "erro":
            "Erro ao salvar"

        }

    except Exception as e:

        db.rollback()

        return {

            "erro":
            str(e)

        }


# =========================================
# ATIVAR / DESATIVAR
# =========================================

@router.patch(
"/api/formacoes/toggle/{formacao_id}"
)

def toggle_formacao(

    formacao_id:int,
    db:Session=Depends(get_db)

):

    formacao=db.get(
        Formacao,
        formacao_id
    )

    if not formacao:

        raise HTTPException(

            status_code=404,
            detail="Formação não encontrada"

        )

    formacao.ativo=(
        not formacao.ativo
    )

    db.commit()

    return {

        "ok":True,
        "ativo":formacao.ativo

    }


# =========================================
# ENUMS
# =========================================

@router.get("/api/enums")
def enums():

    return {

        "modalidade":[

            "presencial",
            "online",
            "hibrido"

        ],

        "status":[

            "Planejada",
            "Em andamento",
            "Finalizada",
            "Cancelada",
            "Em construção"

        ]

    }
