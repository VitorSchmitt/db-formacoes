from fastapi import APIRouter, Query, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from database import SessionLocal

from models import (
    Participacao,
    Formacao,
    Lotacao,
    PlanoAnual
)

router = APIRouter()


# =====================================
# DB
# =====================================

def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


# =====================================
# FILTRO LOTAÇÕES
# =====================================

@router.get("/api/dashboard/lotacoes")
def listar_lotacoes(
    db: Session = Depends(get_db)
):

    stmt = (

        select(
            Lotacao.tipo
        )

        .distinct()

        .order_by(
            Lotacao.tipo
        )

    )

    result = db.execute(
        stmt
    ).all()

    return [

        {
            "tipo": l.tipo
        }
    
        for l in result
        if l.tipo
    ]


# =====================================
# FILTRO CURSOS
# =====================================

@router.get("/api/dashboard/cursos")
def listar_cursos(
    db: Session = Depends(get_db)
):

    stmt = (

        select(
            Formacao.id,
            Formacao.descricao
        )

        .distinct()

        .order_by(
            Formacao.descricao
        )

    )

    result = db.execute(
        stmt
    ).all()

    return [

        {
            "id": c.id,
            "descricao": c.descricao
        }

        for c in result
    ]


# =====================================
# FILTRO EIXOS
# =====================================

@router.get("/api/dashboard/eixos")
def listar_eixos(
    db: Session = Depends(get_db)
):

    stmt = (

        select(
            PlanoAnual.eixo
        )

        .distinct()

        .order_by(
            PlanoAnual.eixo
        )

    )

    result = db.execute(
        stmt
    ).all()

    return [
    
        {
            "eixo": e.eixo
        }
    
        for e in result
        if e.eixo
    ]


# =====================================
# DASHBOARD
# =====================================

@router.get("/api/dashboard")
def dashboard(

    mes_inicio: str = Query(None),
    mes_fim: str = Query(None),
    lotacao: str = Query(None),
    curso: str = Query(None),
    eixo: str = Query(None),

    db: Session = Depends(get_db)

):

    try:

        # =====================================
        # BASE
        # =====================================

        base = (

            db.query(

                Participacao,
                Formacao,
                Lotacao,
                PlanoAnual

            )

            .join(

                Formacao,
                Participacao.formacao_id == Formacao.id

            )

            .join(

                Lotacao,
                Participacao.lotacao_id == Lotacao.id

            )

            .outerjoin(

                PlanoAnual,
                Formacao.plano_id == PlanoAnual.id

            )

        )


        # =====================================
        # FILTROS
        # =====================================

        if mes_inicio:

            base = base.filter(

                func.to_char(
                    Formacao.data_termino,
                    "YYYY-MM"
                ) >= mes_inicio

            )


        if mes_fim:

            base = base.filter(

                func.to_char(
                    Formacao.data_termino,
                    "YYYY-MM"
                ) <= mes_fim

            )


        if lotacao:

            base = base.filter(
                Lotacao.tipo == lotacao
            )


        if curso:

            base = base.filter(
                Formacao.descricao == curso
            )


        if eixo:

            base = base.filter(
                PlanoAnual.eixo == eixo
            )


        # =====================================
        # PARTICIPAÇÕES
        # =====================================

        participacoes = base.all()

        total = len(
            participacoes
        )

        certificados = 0
        carga_realizada = 0


        for p,f,l,pa in participacoes:

            carga = (

                p.aproveitamento
                or 0

            )

            carga_realizada += carga

            carga_total = (

                f.carga_horaria
                or 0

            )

            percentual = 0

            if carga_total > 0:

                percentual = (

                    carga
                    /
                    carga_total

                ) * 100


            if percentual >= 75:

                certificados += 1


        evasao = (
            total-certificados
        )
        
        taxa_evasao = (

            round(
                (evasao / total) * 100,
                2
            )
        
            if total > 0
            else 0
        )


        servidores_unicos = len(

            set(

                p.matricula

                for p,f,l,pa
                in participacoes

            )

        )


        media = (

            round(
                total/servidores_unicos,
                2
            )

            if servidores_unicos
            else 0
        )


        # =====================================
        # LOTAÇÕES
        # =====================================

        lotacao_data = (

            base.with_entities(

                Lotacao.tipo,

                func.count(
                    Participacao.id
                )

            )

            .group_by(
                Lotacao.tipo
            )

            .order_by(

                func.count(
                    Participacao.id
                ).desc()

            )

            .all()

        )


        # =====================================
        # CURSOS
        # =====================================
        curso_data = (
        
            base.with_entities(
        
                Formacao.id,
        
                Formacao.descricao,
        
                func.count(
                    Participacao.id
                ).label(
                    "qtd"
                )
        
            )
        
            .group_by(
        
                Formacao.id,
        
                Formacao.descricao
        
            )
        
            .order_by(
        
                func.count(
                    Participacao.id
                ).desc()
        
            )
        
            .all()
        
        )


        # =====================================
        # PERÍODO
        # =====================================

        periodo_data = (

            base.with_entities(

                func.to_char(

                    Formacao.data_termino,
                    "YYYY-MM"

                ),

                func.count(
                    Participacao.id
                )

            )

            .group_by(

                func.to_char(
                    Formacao.data_termino,
                    "YYYY-MM"
                )

            )

            .order_by(

                func.to_char(
                    Formacao.data_termino,
                    "YYYY-MM"
                )

            )

            .all()

        )


        return {

            "cards":{

                "participacoes": total,
                "certificados": certificados,
                "evasao": evasao,
                "taxa_evasao": taxa_evasao,
                "servidores_unicos": servidores_unicos,
                "carga_realizada": carga_realizada,
                "media_por_servidor": media

            },

            "lotacao":[

                {
                    "lotacao":l[0],
                    "qtd":l[1]
                }

                for l in lotacao_data
            ],

            "curso":[
            
                {
                    "formacao": c[1],
                    "qtd": c[2]
                }
            
                for c in curso_data
            ],

            "periodo":[

                {
                    "mes":p[0],
                    "qtd":p[1]
                }

                for p in periodo_data
            ]

        }

    except Exception as e:

        import traceback
        traceback.print_exc()

        return {
            "erro":str(e)
        }
