from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from database import get_db
from model_estagiario import ClassificacaoEstagio


router = APIRouter(
    prefix="/api/classificacoes-estagio",
    tags=["Classificações Estágio"]
)



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
        "classificacoes/lista.html",
        {
            "request": request,
            "classificacoes": classificacoes
        }
    )



@router.get("/novo")
def novo(
    request: Request
):

    return request.app.state.templates.TemplateResponse(
        "classificacoes/form.html",
        {
            "request": request
        }
    )



@router.post("/novo")
def criar(
    codigo: str = Form(...),
    descricao: str = Form(...),
    db: Session = Depends(get_db)
):

    classificacao = ClassificacaoEstagio(
        codigo=codigo,
        descricao=descricao
    )

    db.add(classificacao)
    db.commit()


    return RedirectResponse(
        "/classificacoes-estagio/",
        status_code=303
    )



@router.get("/{id}/editar")
def editar(
    id: int,
    request: Request,
    db: Session = Depends(get_db)
):

    classificacao = (
        db.query(ClassificacaoEstagio)
        .filter(
            ClassificacaoEstagio.id == id
        )
        .first()
    )


    return request.app.state.templates.TemplateResponse(
        "classificacoes/form.html",
        {
            "request": request,
            "classificacao": classificacao
        }
    )



@router.post("/{id}/editar")
def atualizar(
    id: int,
    codigo: str = Form(...),
    descricao: str = Form(...),
    ativo: bool = Form(False),
    db: Session = Depends(get_db)
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
        "/classificacoes-estagio/",
        status_code=303
    )
