from fastapi import APIRouter, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from database import SessionLocal

from models import (
    Participacao,
    Formacao,
    Lotacao
)

router = APIRouter()


# =========================================
# DASHBOARD
# =========================================
@router.get("/api/dashboard")
def dashboard(

    mes_inicio: str = Query(None),
    mes_fim: str = Query(None),
    lotacao: str = Query(None),
    curso: str = Query(None),
    eixo: str = Query(None),

):

    db = SessionLocal()

    try:

        # =====================================
        # QUERY BASE
        # =====================================

        base = (

            db.query(
                Participacao,
                Formacao,
                Lotacao
            )

            .join(
                Formacao,
                Participacao.formacao_id == Formacao.id
            )

            .join(
                Lotacao,
                Participacao.lotacao_id == Lotacao.id
            )
        )


        # =====================================
        # FILTROS
        # =====================================

        if mes_inicio:

            base = base.filter(

                func.to_char(
                    Formacao.data_termino,
                    'YYYY-MM'
                ) >= mes_inicio
            )

        if mes_fim:

            base = base.filter(

                func.to_char(
                    Formacao.data_termino,
                    'YYYY-MM'
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
                Formacao.eixo == eixo
            )


        # =====================================
        # PARTICIPAÇÕES
        # =====================================

        participacoes = base.all()

        total = len(participacoes)


        # =====================================
        # CERTIFICADOS
        # =====================================

        certificados = 0

        carga_realizada_total = 0

        for p, f, l in participacoes:

            carga_total = (
                f.carga_horaria or 0
            )

            carga_realizada = (
                p.aproveitamento or 0
            )

            carga_realizada_total += (
                carga_realizada or 0
            )

            percentual = 0

            if carga_total > 0:

                percentual = round(
                    (
                        carga_realizada /
                        carga_total
                    ) * 100,
                    2
                )

            if percentual >= 75:

                certificados += 1


        # =====================================
        # EVASÃO
        # =====================================

        evasao = (
            total - certificados
        )


        # =====================================
        # TAXA EVASÃO
        # =====================================

        taxa_evasao = 0

        if total > 0:

            taxa_evasao = round(
                (
                    evasao / total
                ) * 100,
                2
            )


        # =====================================
        # MÉDIA POR SERVIDOR
        # =====================================

        servidores_unicos = len(

            set(

                [
                    p.matricula
                    for p, f, l
                    in participacoes
                ]
            )
        )

        media_por_servidor = 0

        if servidores_unicos > 0:

            media_por_servidor = round(
                total /
                servidores_unicos,
                2
            )


        # =====================================
        # LOTAÇÕES
        # =====================================

        lotacao_data = (

            base.with_entities(

                Lotacao.tipo,

                func.count()

            )

            .group_by(
                Lotacao.tipo
            )

            .order_by(
                func.count().desc()
            )

            .all()
        )


        # =====================================
        # CURSOS
        # =====================================

        curso_data = (

            base.with_entities(

                Formacao.descricao,

                func.count()

            )

            .group_by(
                Formacao.descricao
            )

            .order_by(
                func.count().desc()
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
                    'YYYY-MM'
                ),

                func.count()

            )

            .group_by(

                func.to_char(
                    Formacao.data_termino,
                    'YYYY-MM'
                )
            )

            .order_by(

                func.to_char(
                    Formacao.data_termino,
                    'YYYY-MM'
                )
            )

            .all()
        )


        # =====================================
        # EIXOS
        # =====================================

        eixo_data = (

            base.with_entities(

                Formacao.eixo,

                func.count()

            )

            .group_by(
                Formacao.eixo
            )

            .order_by(
                func.count().desc()
            )

            .all()
        )


        # =====================================
        # PERÍODO X EIXO
        # =====================================

        periodo_eixo_data = (

            base.with_entities(

                func.to_char(
                    Formacao.data_termino,
                    'YYYY-MM'
                ),

                Formacao.eixo,

                func.count()

            )

            .group_by(

                func.to_char(
                    Formacao.data_termino,
                    'YYYY-MM'
                ),

                Formacao.eixo
            )

            .order_by(

                func.to_char(
                    Formacao.data_termino,
                    'YYYY-MM'
                )
            )

            .all()
        )


        # =====================================
        # ANUAL
        # =====================================

        anual_data = (

            base.with_entities(

                func.extract(
                    'year',
                    Formacao.data_termino
                ),

                func.count()

            )

            .group_by(

                func.extract(
                    'year',
                    Formacao.data_termino
                )
            )

            .order_by(

                func.extract(
                    'year',
                    Formacao.data_termino
                )
            )

            .all()
        )


        # =====================================
        # RESPONSE
        # =====================================

        return {

            # =================================
            # CARDS
            # =================================

            "cards": {

                "participacoes":
                    total,

                "certificados":
                    certificados,

                "evasao":
                    evasao,

                "taxa_evasao":
                    taxa_evasao,

                "carga_realizada":
                    carga_realizada_total,

                "media_por_servidor":
                    media_por_servidor
            },


            # =================================
            # LOTAÇÃO
            # =================================

            "lotacao": [

                {
                    "lotacao": l[0],
                    "qtd": l[1]
                }

                for l in lotacao_data
            ],


            # =================================
            # CURSOS
            # =================================

            "curso": [

                {
                    "formacao": c[0],
                    "qtd": c[1]
                }

                for c in curso_data
            ],


            # =================================
            # PERÍODO
            # =================================

            "periodo": [

                {
                    "mes": p[0],
                    "qtd": p[1]
                }

                for p in periodo_data
            ],


            # =================================
            # EIXOS
            # =================================

            "eixo": [

                {
                    "eixo": e[0],
                    "qtd": e[1]
                }

                for e in eixo_data
            ],


            # =================================
            # PERÍODO X EIXO
            # =================================

            "periodo_eixo": [

                {
                    "mes": p[0],
                    "eixo": p[1],
                    "qtd": p[2]
                }

                for p in periodo_eixo_data
            ],


            # =================================
            # ANUAL
            # =================================

            "anual": [

                {
                    "ano": int(a[0]),
                    "qtd": a[1]
                }

                for a in anual_data
            ]
        }

    except Exception as e:

        import traceback

        traceback.print_exc()

        return {
            "erro": str(e)
        }

    finally:

        db.close()
