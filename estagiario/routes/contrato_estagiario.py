from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from estagiario.model_estagiario  import ContratoEstagio
from schemas import ContratoEstagioSchema

router_contrato = APIRouter(prefix="/api/contratos_estagio", tags=["Contratos de Estágio"])

@router_contrato.get("/", response_model=List[dict])
def listar_contratos(db: Session = Depends(get_db)):
    contratos = db.query(ContratoEstagio).all()
    return [
        {
            "id": c.id,
            "numero_contrato": c.numero_contrato,
            "estagiario_id": c.estagiario_id,
            "estagiario_nome": c.estagiario.nome if c.estagiario else "Não informado",
            "lotacao_id": c.lotacao_id,
            "lotacao_descricao": c.lotacao.descricao if c.lotacao else "Não informada",
            "supervisor_matricula": c.supervisor_matricula,
            "supervisor_nome": c.supervisor.nome if c.supervisor else "Não informado",
            "classificacao_id": c.classificacao_id,
            "classificacao_descricao": c.classificacao.descricao if c.classificacao else "Não informada",
            "beneficio_id": c.beneficio_id,
            "data_inicio": c.data_inicio.strftime("%Y-%m-%d"),
            "data_fim": c.data_fim.strftime("%Y-%m-%d"),
            "carga_horaria_diaria": c.carga_horaria_diaria,
            "horario": c.horario,
            "data_assinatura": c.data_assinatura.strftime("%Y-%m-%d"),
            "observacoes": c.observacoes,
            "data_desligamento": c.data_desligamento.strftime("%Y-%m-%d") if c.data_desligamento else None,
            "motivo_desligamento": c.motivo_desligamento,
            "observacao_desligamento": c.observacao_desligamento
        } for c in contratos
    ]

@router_contrato.post("/", status_code=status.HTTP_201_CREATED)
def criar_contrato(dados: ContratoEstagioSchema, db: Session = Depends(get_db)):
    existe = db.query(ContratoEstagio).filter(ContratoEstagio.numero_contrato == dados.numero_contrato).first()
    if existe:
        raise HTTPException(status_code=400, detail="Número de contrato já existente.")
    
    novo = ContratoEstagio(**dados.model_dump())
    db.add(novo)
    db.commit()
    return {"mensagem": "Contrato cadastrado com sucesso"}

@router_contrato.put("/{id}")
def atualizar_contrato(id: int, dados: ContratoEstagioSchema, db: Session = Depends(get_db)):
    contrato = db.query(ContratoEstagio).filter(ContratoEstagio.id == id).first()
    if not contrato:
        raise HTTPException(status_code=404, detail="Contrato não encontrado")
    
    conflito = db.query(ContratoEstagio).filter(
        ContratoEstagio.numero_contrato == dados.numero_contrato, 
        ContratoEstagio.id != id
    ).first()
    if conflito:
        raise HTTPException(status_code=400, detail="Outro contrato já utiliza este número.")

    for key, value in dados.model_dump().items():
        setattr(contrato, key, value)
        
    db.commit()
    return {"mensagem": "Contrato atualizado com sucesso"}

@router_contrato.post("/{id}/desligar")
def desligar_contrato(id: int, dados: ContratoEstagioSchema, db: Session = Depends(get_db)):
    contrato = db.query(ContratoEstagio).filter(ContratoEstagio.id == id).first()
    if not contrato:
        raise HTTPException(status_code=404, detail="Contrato não encontrado")
    
    contrato.data_desligamento = dados.data_desligamento
    contrato.motivo_desligamento = dados.motivo_desligamento
    contrato.observacao_desligamento = dados.observacao_desligamento
    
    db.commit()
    return {"mensagem": "Contrato encerrado com sucesso"}
