from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from database import get_db
from model_estagiario import ClassificacaoEstagio


router = APIRouter(
    prefix="/estagiario/classificacoes",
    tags=["Classificações Estágio"]
)



# ===============================
# LISTAGEM
# ===============================

@router.get("/")
def listar(
    request: Request,
    db: Session = Depends(get_db)
):

    classificacoes = (
        db.query(ClassificacaoEstagio)
        .order_by(
            ClassificacaoEstagio.codigo
        )
        .all()
    )


    return request.app.state.templates.TemplateResponse(
        "estagiario/classificacoes.html",
        {
            "request": request,
            "classificacoes": classificacoes
        }
    )



# ===============================
# NOVO FORM
# ===============================

@router.get("/novo")
def novo(
    request: Request
):

    return request.app.state.templates.TemplateResponse(
        "estagiario/classificacao_form.html",
        {
            "request":request
        }
    )



# ===============================
# SALVAR
# ===============================

@router.post("/novo")
def criar(
    codigo:str = Form(...),
    descricao:str = Form(...),
    db:Session = Depends(get_db)
):


    existe = (
        db.query(ClassificacaoEstagio)
        .filter(
            ClassificacaoEstagio.codigo == codigo
        )
        .first()
    )


    if existe:
        return RedirectResponse(
            "/estagiario/classificacoes/novo?erro=duplicado",
            status_code=303
        )



    classificacao = ClassificacaoEstagio(
        codigo=codigo,
        descricao=descricao,
        ativo=True
    )


    db.add(classificacao)
    db.commit()


    return RedirectResponse(
        "/estagiario/classificacoes/",
        status_code=303
    )



# ===============================
# EDITAR FORM
# ===============================

@router.get("/{id}/editar")
def editar(
    id:int,
    request:Request,
    db:Session=Depends(get_db)
):


    classificacao = (
        db.query(ClassificacaoEstagio)
        .filter(
            ClassificacaoEstagio.id == id
        )
        .first()
    )


    if not classificacao:
        raise HTTPException(
            status_code=404,
            detail="Classificação não encontrada"
        )



    return request.app.state.templates.TemplateResponse(
        "estagiario/classificacao_form.html",
        {
            "request":request,
            "classificacao":classificacao
        }
    )



# ===============================
# ATUALIZAR
# ===============================

@router.post("/{id}/editar")
def atualizar(
    id:int,
    codigo:str=Form(...),
    descricao:str=Form(...),
    ativo:str=Form(None),
    db:Session=Depends(get_db)
):


    classificacao = (
        db.query(ClassificacaoEstagio)
        .filter(
            ClassificacaoEstagio.id == id
        )
        .first()
    )


    if not classificacao:
        raise HTTPException(
            status_code=404,
            detail="Registro não encontrado"
        )



    classificacao.codigo = codigo
    classificacao.descricao = descricao
    classificacao.ativo = ativo == "on"



    db.commit()



    return RedirectResponse(
        "/estagiario/classificacoes/",
        status_code=303
    )



# ===============================
# ALTERAR STATUS
# ===============================

@router.get("/{id}/status")
def alterar_status(
    id:int,
    db:Session=Depends(get_db)
):


    classificacao = (
        db.query(ClassificacaoEstagio)
        .filter(
            ClassificacaoEstagio.id == id
        )
        .first()
    )


    if not classificacao:
        raise HTTPException(
            status_code=404,
            detail="Registro não encontrado"
        )


    classificacao.ativo = not classificacao.ativo

    db.commit()



    return RedirectResponse(
        "/estagiario/classificacoes/",
        status_code=303
    )
