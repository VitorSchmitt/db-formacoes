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
                    str(f.status)
                    if f.status
                    else None,

                "plano_id":
                    f.plano_id,

                "ativo":
                    f.ativo

            }

            for f in dados

        ],

        "total":
            total,

        "total_paginas":

            (total // limite)
            +
            (1 if total % limite else 0)

    }


# =========================================
# CRIAR
# =========================================

@router.post("/api/formacao")
def criar(
    dados: dict,
    db: Session = Depends(get_db)
):

    # ============================
    # CAMPOS OBRIGATÓRIOS
    # ============================

    campos_obrigatorios = {

        "descricao": "Descrição",
        "data_inicio": "Data início",
        "data_termino": "Data término",
        "carga_horaria": "Carga horária",
        "modalidade": "Modalidade",        
        "publico_alvo": "Público-alvo",
        "meta_participantes": "Meta participantes",
        "investimento": "Investimento",
        "status": "Status",
        "plano_id": "Plano anual"

    }

    faltando = []

    for chave, nome in campos_obrigatorios.items():

        valor = dados.get(chave)

        if valor is None:

            faltando.append(nome)

        elif isinstance(valor, str):

            if valor.strip() == "":
                faltando.append(nome)

    if faltando:

        return {

            "erro":
            "Preencha os campos: "
            + ", ".join(faltando)

        }

    # ============================
    # DUPLICIDADE
    # ============================

    existe = (

        db.query(Formacao)

        .filter(

            Formacao.descricao ==
            dados.get("descricao"),

            Formacao.data_termino ==
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

            descricao=dados.get("descricao"),
            data_inicio=dados.get("data_inicio"),
            data_termino=dados.get("data_termino"),            
            carga_horaria=dados.get("carga_horaria"),
            modalidade=dados.get("modalidade"),
            publico_alvo=dados.get("publico_alvo"),
            investimento=dados.get("investimento"),
            meta_participantes=dados.get("meta_participantes"),
            status=dados.get("status"),
            plano_id=dados.get("plano_anual_id"),
            ativo=True

        )

        db.add(nova)

        db.commit()

        db.refresh(nova)

        return {

            "ok": True,
            "message": "Formação cadastrada",
            "id": nova.id

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

    formacao = db.get(
        Formacao,
        id
    )

    if not formacao:

        return {

            "erro":
            "Formação não encontrada"

        }

    try:

        for campo, valor in (

            dados.dict(
                exclude_unset=True
            ).items()

        ):

            setattr(
                formacao,
                campo,
                valor
            )

        db.commit()

        db.refresh(formacao)

        return {

            "ok": True,
            "message": "Formação atualizada"

        }

    except IntegrityError:

        db.rollback()

        return {

            "erro":
            "Erro ao atualizar"

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

    db.refresh(formacao)

    return {

        "ok": True,
        "ativo": formacao.ativo

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
            "Finalizada",
            "Cancelada",
            "Em construção"

        ]

    }
