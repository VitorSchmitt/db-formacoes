from fastapi import APIRouter, Depends, HTTPException, status,Request
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from estagiario.model_estagiario import ContratoEstagio
from schemas import ContratoEstagioCreate, ContratoEstagioUpdate, DesligamentoContratoInput

router = APIRouter(prefix="/api/contrato_estagio", tags=["Contratos de Estágio"])

@router.get("/", response_model=List[dict])
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
            "data_inicio": c.data_inicio.strftime("%Y-%m-%d"),
            "data_fim": c.data_fim.strftime("%Y-%m-%d"),
            "carga_horaria_diaria": c.carga_horaria_diaria,
            "horario": c.horario,
            "vale_alimentacao": c.vale_alimentacao,
            "quantidade_vale_transporte": c.quantidade_vale_transporte,
            "data_assinatura": c.data_assinatura.strftime("%Y-%m-%d"),
            "observacoes": c.observacoes,
            "data_desligamento": c.data_desligamento.strftime("%Y-%m-%d") if c.data_desligamento else None,
            "motivo_desligamento": c.motivo_desligamento,
            "observacao_desligamento": c.observacao_desligamento
        } for c in contratos
    ]

@router.post("/", status_code=status.HTTP_201_CREATED)
def criar_contrato(dados: ContratoEstagioCreate, db: Session = Depends(get_db)):
    existe = db.query(ContratoEstagio).filter(ContratoEstagio.numero_contrato == dados.numero_contrato).first()
    if existe:
        raise HTTPException(status_code=400, detail="Número de contrato já existente.")
    
    novo = ContratoEstagio(**dados.model_dump())
    db.add(novo)
    db.commit()
    return {"mensagem": "Contrato cadastrado com sucesso"}

@router.put("/{id}")
def atualizar_contrato(id: int, dados: ContratoEstagioUpdate, db: Session = Depends(get_db)):
    contrato = db.query(ContratoEstagio).filter(ContratoEstagio.id == id).first()
    if not contrato:
        raise HTTPException(status_code=404, detail="Contrato não encontrado")
    
    if dados.numero_contrato:
        conflito = db.query(ContratoEstagio).filter(
            ContratoEstagio.numero_contrato == dados.numero_contrato, 
            ContratoEstagio.id != id
        ).first()
        if conflito:
            raise HTTPException(status_code=400, detail="Outro contrato já utiliza este número.")

    # Atualiza apenas os campos que foram enviados na requisição
    dados_atualizados = dados.model_dump(exclude_unset=True)
    for key, value in dados_atualizados.items():
        setattr(contrato, key, value)
        
    db.commit()
    return {"mensagem": "Contrato atualizado com sucesso"}

@router.post("/{id}/desligar")
def desligar_contrato(id: int, dados: DesligamentoContratoInput, db: Session = Depends(get_db)):
    contrato = db.query(ContratoEstagio).filter(ContratoEstagio.id == id).first()
    if not contrato:
        raise HTTPException(status_code=404, detail="Contrato não encontrado")
    
    contrato.data_desligamento = dados.data_desligamento
    contrato.motivo_desligamento = dados.motivo_desligamento
    contrato.observacao_desligamento = dados.observacao_desligamento
    
    db.commit()
    return {"mensagem": "Contrato encerrado com sucesso"}


@router.get("/meus", response_model=List[dict])
def listar_meus_contratos(
    request: Request,
    db: Session = Depends(get_db)
):
    usuario_logado = request.session.get("user")

    if not usuario_logado:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não autenticado."
        )

    matricula = usuario_logado.get("matricula")

    contratos = (
        db.query(ContratoEstagio)
        .filter(
            ContratoEstagio.supervisor_matricula == matricula
        )
        .all()
    )

    return [
        {
            "id": c.id,
            "numero_contrato": c.numero_contrato,
            "estagiario_nome": c.estagiario.nome if c.estagiario else "Não informado"
        }
        for c in contratos
    ]
