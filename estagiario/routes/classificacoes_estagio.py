from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from database import get_db
from model_estagiario import ClassificacaoEstagio


router = APIRouter(
    prefix="/estagiario/classificacoes",
    tags=["Classificações Estágio"]
)



# LISTAGEM HTML

@router.get("/")
def listar(
    request: Request,
    db: Session = Depends(get_db)
):

    classificacoes = (
        db.query(ClassificacaoEstagio)
        .order_by(ClassificacaoEstagio.codigo)
        .all()
    )


    return request.app.state.templates.TemplateResponse(
        "estagiario/classificacoes.html",
        {
            "request": request,
            "classificacoes": classificacoes
        }
    )



# NOVO

@router.get("/novo")
def novo(
    request: Request
):

    return request.app.state.templates.TemplateResponse(
        "estagiario/classificacao_form.html",
        {
            "request": request
        }
    )



# SALVAR NOVO

@router.post("/novo")
def criar(
    codigo: str = Form(...),
    descricao: str = Form(...),
    db: Session = Depends(get_db)
):


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



# EDITAR

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


    return request.app.state.templates.TemplateResponse(
        "estagiario/classificacao_form.html",
        {
            "request":request,
            "classificacao":classificacao
        }
    )



# ATUALIZAR

@router.post("/{id}/editar")
def atualizar(
    id:int,
    codigo:str=Form(...),
    descricao:str=Form(...),
    ativo:bool=Form(False),
    db:Session=Depends(get_db)
):


    classificacao = (
        db.query(ClassificacaoEstagio)
        .filter(
            ClassificacaoEstagio.id == id
        )
        .first()
    )


    classificacao.codigo = codigo
    classificacao.descricao = descricao
    classificacao.ativo = ativo


    db.commit()


    return RedirectResponse(
        "/estagiario/classificacoes/",
        status_code=303
    )



# ATIVAR / INATIVAR

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


    classificacao.ativo = not classificacao.ativo


    db.commit()


    return RedirectResponse(
        "/estagiario/classificacoes/",
        status_code=303
    )
