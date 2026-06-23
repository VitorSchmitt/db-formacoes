from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from estagiario.model_estagiario import Estagiario  # Ajuste o caminho conforme seu projeto
from schemas import EstagiarioSchema

router = APIRouter(
    prefix="/api/estagiarios",
    tags=["Estagiários"]
)

# LISTAGEM
@router.get("/", response_model=List[dict])
def listar(db: Session = Depends(get_db)):
    try:
        estagiarios = db.query(Estagiario).order_by(Estagiario.nome).all()
        return [
            {
                "id": e.id,
                "nome": e.nome,
                "sexo": e.sexo.name if hasattr(e.sexo, 'name') else str(e.sexo),
                "cpf": e.cpf,
                "data_nascimento": e.data_nascimento.strftime("%Y-%m-%d") if e.data_nascimento else "",
                "email": e.email or "",
                "telefone": e.telefone or "",
                "endereco": e.endereco or "",
                "instituicao_ensino": e.instituicao_ensino or "",
                "curso": e.curso or "",
                "semestre": e.semestre or "",
                "ativo": e.ativo,
                "observacoes": e.observacoes or "",
                "nome_responsavel": e.nome_responsavel or "",
                "cpf_responsavel": e.cpf_responsavel or "",
                "parentesco_responsavel": e.parentesco_responsavel or "",
                "telefone_responsavel": e.telefone_responsavel or "",
                "email_responsavel": e.email_responsavel or ""
            }
            for e in estagiarios
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar estagiários: {str(e)}")

# SALVAR (POST)
@router.post("/", status_code=status.HTTP_201_CREATED)
def criar(dados: EstagiarioSchema, db: Session = Depends(get_db)):
    # Remove pontos e traços do CPF para evitar problemas de formatação no banco
    cpf_limpo = dados.cpf.replace(".", "").replace("-", "").strip()

    existe = db.query(Estagiario).filter(Estagiario.cpf == cpf_limpo).first()
    if existe:
        raise HTTPException(status_code=400, detail="Este CPF já está cadastrado para outro estagiário.")

    try:
        novo_estagiario = Estagiario(
            nome=dados.nome.strip(),
            sexo=dados.sexo,
            cpf=cpf_limpo,
            data_nascimento=dados.data_nascimento,
            email=dados.email,
            telefone=dados.telefone,
            endereco=dados.endereco,
            instituicao_ensino=dados.instituicao_ensino,
            curso=dados.curso,
            semestre=dados.semestre,
            ativo=dados.ativo,
            observacoes=dados.observacoes,
            nome_responsavel=dados.nome_responsavel,
            cpf_responsavel=dados.cpf_responsavel,
            parentesco_responsavel=dados.parentesco_responsavel,
            telefone_responsavel=dados.telefone_responsavel,
            email_responsavel=dados.email_responsavel
        )
        db.add(novo_estagiario)
        db.commit()
        return {"mensagem": "Estagiário criado com sucesso"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao salvar estagiário: {str(e)}")

# ATUALIZAR (PUT)
@router.put("/{id}")
def atualizar(id: int, dados: EstagiarioSchema, db: Session = Depends(get_db)):
    estagiario = db.query(Estagiario).filter(Estagiario.id == id).first()
    if not estagiario:
        raise HTTPException(status_code=404, detail="Estagiário não encontrado")

    cpf_limpo = dados.cpf.replace(".", "").replace("-", "").strip()
    
    cpf_duplicado = db.query(Estagiario).filter(Estagiario.cpf == cpf_limpo, Estagiario.id != id).first()
    if cpf_duplicado:
        raise HTTPException(status_code=400, detail="Este CPF já está em uso por outro estagiário.")

    try:
        estagiario.nome = dados.nome.strip()
        estagiario.sexo = dados.sexo
        estagiario.cpf = cpf_limpo
        estagiario.data_nascimento = dados.data_nascimento
        estagiario.email = dados.email
        estagiario.telefone = dados.telefone
        estagiario.endereco = dados.endereco
        estagiario.instituicao_ensino = dados.instituicao_ensino
        estagiario.curso = dados.curso
        estagiario.semestre = dados.semestre
        estagiario.ativo = dados.ativo
        estagiario.observacoes = dados.observacoes
        estagiario.nome_responsavel = dados.nome_responsavel
        estagiario.cpf_responsavel = dados.cpf_responsavel
        estagiario.parentesco_responsavel = dados.parentesco_responsavel
        estagiario.telefone_responsavel = dados.telefone_responsavel
        estagiario.email_responsavel = dados.email_responsavel

        db.commit()
        return {"mensagem": "Estagiário atualizado com sucesso"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar estagiário: {str(e)}")
