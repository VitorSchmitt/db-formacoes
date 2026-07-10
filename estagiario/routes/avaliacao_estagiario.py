from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from database import get_db
from estagiario.model_acompanhamento import AvaliacaoSupervisor
from schemas import (
    AvaliacaoSupervisorCreate,
    AvaliacaoSupervisorUpdate
)

router = APIRouter(
    prefix="/api/avaliacao_estagiario",
    tags=["Avaliação do Supervisor"]
)


# ==========================
# LISTAR
# ==========================
@router.get("/")
def listar(db: Session = Depends(get_db), limit: int = 100, offset: int = 0):
    # CORRIGIDO: Removido o return precoce.
    # O joinedload carrega o relacionamento 'contrato' de uma só vez (evita o problema N+1)
    resultados = (
        db.query(AvaliacaoSupervisor)
        .options(joinedload(AvaliacaoSupervisor.contrato))  # Garante performance no join
        .order_by(AvaliacaoSupervisor.data_avaliacao.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    
    # Monta a resposta exatamente no formato esperado pelo front-end
    lista_formatada = []
    for av in resultados:
        contrato = getattr(av, 'contrato', None)
        # Busca o objeto estagiario de dentro do contrato
        estagiario = getattr(contrato, 'estagiario', None) if contrato else None
        
        lista_formatada.append({
            "id": av.id,
            "contrato_id": av.contrato_id,
            "data_avaliacao": av.data_avaliacao.isoformat() if hasattr(av.data_avaliacao, 'isoformat') else str(av.data_avaliacao),
            "avaliacao": av.avaliacao,
            "parecer": av.parecer,
            
            # Buscando o número do contrato
            "numero_contrato": contrato.numero_contrato if contrato else f"Contrato #{av.contrato_id}",
            
            # CORRIGIDO: Agora busca corretamente o nome de dentro da classe Estagiario
            "estagiario_nome": estagiario.nome if estagiario else "Não informado"
        })
        
    return lista_formatada


# ==========================
# BUSCAR POR ID
# ==========================
@router.get("/{id}")
def buscar(id: int, db: Session = Depends(get_db)): 

    avaliacao = (
        db.query(AvaliacaoSupervisor)
        .filter(AvaliacaoSupervisor.id == id)
        .first()
    )

    if not avaliacao:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Avaliação não encontrada."
        )

    return avaliacao


# ==========================
# INSERIR
# ==========================
@router.post("/", status_code=status.HTTP_201_CREATED)
def inserir(
    dados: AvaliacaoSupervisorCreate,
    db: Session = Depends(get_db)
):

    avaliacao = AvaliacaoSupervisor(
        contrato_id=dados.contrato_id,
        data_avaliacao=dados.data_avaliacao,
        avaliacao=dados.avaliacao,
        parecer=dados.parecer
    )

    db.add(avaliacao)
    db.commit()
    db.refresh(avaliacao)

    return avaliacao


# ==========================
# ALTERAR
# ==========================
@router.put("/{id}")
def alterar(
    id: int,
    dados: AvaliacaoSupervisorUpdate,
    db: Session = Depends(get_db)
):

    avaliacao = (
        db.query(AvaliacaoSupervisor)
        .filter(AvaliacaoSupervisor.id == id)
        .first()
    )

    if not avaliacao:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Avaliação não encontrada."
        )

    # Refatorado: Atualização dinâmica usando setattr (evita uma pilha de IFs)
    # Exclui campos não enviados na requisição (útil se o schema aceitar campos opcionais)
    dados_atualizar = dados.model_dump(exclude_unset=True) if hasattr(dados, 'model_dump') else dados.dict(exclude_unset=True)
    
    for chave, valor in dados_atualizar.items():
        setattr(avaliacao, chave, valor)

    db.commit()
    db.refresh(avaliacao)

    return avaliacao


# ==========================
# EXCLUIR
# ==========================
@router.delete("/{id}")
def excluir(
    id: int,
    db: Session = Depends(get_db)
):

    avaliacao = (
        db.query(AvaliacaoSupervisor)
        .filter(AvaliacaoSupervisor.id == id)
        .first()
    )

    if not avaliacao:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Avaliação não encontrada."
        )

    db.delete(avaliacao)
    db.commit()

    return {
        "mensagem": "Avaliação excluída com sucesso."
    }
