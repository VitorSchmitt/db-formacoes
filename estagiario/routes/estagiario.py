from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from estagiario.model_estagiario import Estagiario  
from schemas import EstagiarioSchema

router = APIRouter(
    prefix="/api/estagiarios",
    tags=["Estagiários"]
)

# Função auxiliar para garantir Caixa Alta e tratar valores nulos/vazios
def tratar_texto(valor: str, padrao: str = "NÃO INFORMADO") -> str:
    if not valor or not str(valor).strip():
        return padrao.upper()
    return str(valor).strip().upper()

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
                "nome_responsavel": e.nome_responsavel or "NÃO INFORMADO",
                "cpf_responsavel": e.cpf_responsavel or "NÃO INFORMADO",
                "parentesco_responsavel": e.parentesco_responsavel or "NÃO INFORMADO",
                "telefone_responsavel": e.telefone_responsavel or "NÃO INFORMADO",
                "email_responsavel": e.email_responsavel or "NÃO INFORMADO"
            }
            for e in estagiarios
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar estagiários: {str(e)}")

# SALVAR (POST)
@router.post("/", status_code=status.HTTP_201_CREATED)
def criar(dados: EstagiarioSchema, db: Session = Depends(get_db)):
    cpf_limpo = dados.cpf.replace(".", "").replace("-", "").strip()

    existe = db.query(Estagiario).filter(Estagiario.cpf == cpf_limpo).first()
    if existe:
        raise HTTPException(status_code=400, detail="Este CPF já está cadastrado para outro estagiário.")

    # Regra do responsável caso venha vazio do Front-end
    tem_responsavel = bool(dados.nome_responsavel and dados.nome_responsavel.strip())
    resp_padrao = "NÃO INFORMADO" if not tem_responsavel else ""

    try:
        novo_estagiario = Estagiario(
            nome=tratar_texto(dados.nome),
            sexo=dados.sexo,
            cpf=cpf_limpo,
            data_nascimento=dados.data_nascimento,
            email=tratar_texto(dados.email),
            telefone=dados.telefone,
            endereco=tratar_texto(dados.endereco),
            instituicao_ensino=tratar_texto(dados.instituicao_ensino),
            curso=tratar_texto(dados.curso),
            semestre=tratar_texto(dados.semestre),
            ativo=dados.ativo,
            observacoes=tratar_texto(dados.observacoes, padrao="") if dados.observacoes else None,
            
            # Tratamento do Responsável
            nome_responsavel=tratar_texto(dados.nome_responsavel, padrao=resp_padrao),
            cpf_responsavel=tratar_texto(dados.cpf_responsavel, padrao=resp_padrao),
            parentesco_responsavel=tratar_texto(dados.parentesco_responsavel, padrao=resp_padrao),
            telefone_responsavel=tratar_texto(dados.telefone_responsavel, padrao=resp_padrao),
            email_responsavel=tratar_texto(dados.email_responsavel, padrao=resp_padrao)
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

    # Regra do responsável caso venha vazio do Front-end
    tem_responsavel = bool(dados.nome_responsavel and dados.nome_responsavel.strip())
    resp_padrao = "NÃO INFORMADO" if not tem_responsavel else ""

    try:
        estagiario.nome = tratar_texto(dados.nome)
        estagiario.sexo = dados.sexo
        estagiario.cpf = cpf_limpo
        estagiario.data_nascimento = dados.data_nascimento
        estagiario.email = tratar_texto(dados.email)
        estagiario.telefone = dados.telefone
        estagiario.endereco = tratar_texto(dados.endereco)
        estagiario.instituicao_ensino = tratar_texto(dados.instituicao_ensino)
        estagiario.curso = tratar_texto(dados.curso)
        estagiario.semestre = tratar_texto(dados.semestre)
        estagiario.ativo = dados.ativo
        estagiario.observacoes = tratar_texto(dados.observacoes, padrao="") if dados.observacoes else None
        
        # Tratamento do Responsável
        estagiario.nome_responsavel = tratar_texto(dados.nome_responsavel, padrao=resp_padrao)
        estagiario.cpf_responsavel = tratar_texto(dados.cpf_responsavel, padrao=resp_padrao)
        estagiario.parentesco_responsavel = tratar_texto(dados.parentesco_responsavel, padrao=resp_padrao)
        estagiario.telefone_responsavel = tratar_texto(dados.telefone_responsavel, padrao=resp_padrao)
        estagiario.email_responsavel = tratar_texto(dados.email_responsavel, padrao=resp_padrao)

        db.commit()
        return {"mensagem": "Estagiário atualizado com sucesso"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar estagiário: {str(e)}")
