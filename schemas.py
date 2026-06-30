from pydantic import BaseModel, EmailStr
from datetime import date
from decimal import Decimal
from typing import Optional
from estagiario.enums import SexoEnum

# ===============================
# FORMAÇÃO
# ===============================

class FormacaoBase(BaseModel):
    descricao: str

    data_inicio: Optional[date] = None
    data_termino: Optional[date] = None    

    carga_horaria: Optional[int] = None
    modalidade: Optional[str] = None
    eixo: Optional[str] = None
    publico_alvo: Optional[str] = None

    investimento: Optional[float] = None
    meta_participantes: Optional[int] = 0

    plano_id: Optional[int] = None
    status: Optional[str] = None

class FormacaoCreate(FormacaoBase):
    pass


class FormacaoUpdate(BaseModel):
    descricao: Optional[str] = None

    data_inicio: Optional[date] = None
    data_termino: Optional[date] = None    

    carga_horaria: Optional[int] = None
    modalidade: Optional[str] = None
    eixo: Optional[str] = None
    publico_alvo: Optional[str] = None

    investimento: Optional[float] = None
    meta_participantes: Optional[int] = None

    plano_id: Optional[int] = None
    status: Optional[str] = None

# ===============================
# SERVIDOR
# ===============================

class ServidorCreate(BaseModel):
    matricula: str
    nome: str
    cargo_id: Optional[int] = None


class ServidorUpdate(BaseModel):
    nome: Optional[str] = None
    cargo_id: Optional[int] = None


# ===============================
# CARGO
# ===============================

class CargoCreate(BaseModel):
    descricao: str


class CargoUpdate(BaseModel):
    descricao: Optional[str] = None


# ===============================
# LOTAÇÃO
# ===============================

class LotacaoCreate(BaseModel):
    descricao: str
    tipo: str


class LotacaoUpdate(BaseModel):
    descricao: Optional[str] = None
    tipo: Optional[str] = None
    ativo: Optional[bool] = None


# ===============================
# PARTICIPAÇÃO
# ===============================

class ParticipacaoCreate(BaseModel):
    matricula: str
    formacao_id: int
    lotacao_id: int
    aproveitamento: Optional[float] = None


class ParticipacaoUpdate(BaseModel):
    lotacao_id: Optional[int] = None
    aproveitamento: Optional[float] = None


# ===============================
# USUÁRIO
# ===============================

class UsuarioCreate(BaseModel):
    username: str
    senha: str
    perfil: str
    email: Optional[str] = None


class UsuarioUpdate(BaseModel):
    username: Optional[str] = None
    senha: Optional[str] = None
    perfil: Optional[str] = None
    email: Optional[str] = None
    ativo: Optional[bool] = None


# ===============================
# LOGIN
# ===============================

class LoginSchema(BaseModel):
    username: str
    senha: str


# ===============================
# PLANO ANUAL
# ===============================

class PlanoAnualCreate(BaseModel):
    ano: int
    eixo: str
    objetivo: Optional[str] = None
    ementa: Optional[str] = None


class PlanoAnualUpdate(BaseModel):
    ano: Optional[int] = None
    eixo: Optional[str] = None
    objetivo: Optional[str] = None
    ementa: Optional[str] = None
    ativo: Optional[bool] = None

class FacilitadorCreate(BaseModel):
    matricula: str
    formacao_id: int

# ===============================
# ESTAGIARIO - CLASSES
# ===============================

# ===============================
# CLASSIFICACAO
# ===============================

class ClassificacaoSchema(BaseModel):
    codigo: str       # Adicionado aqui!
    descricao: str
    ativo: bool

# ===============================
# VALOR BOLSA ESTAGIO
# ===============================
class ValorBolsaSchema(BaseModel):
    classificacao_id: int
    valor_hora: Decimal
    data_inicio_vigencia: date

# ===============================
# ESTAGIARIO
# ===============================

class EstagiarioSchema(BaseModel):
    nome: str
    sexo: SexoEnum  # <--- Agora valida usando o Enum real do Python
    cpf: str
    data_nascimento: Optional[date] = None
    email: Optional[str] = None
    telefone: Optional[str] = None
    endereco: Optional[str] = None
    instituicao_ensino: Optional[str] = None
    curso: Optional[str] = None
    semestre: Optional[str] = None
    ativo: bool = True
    observacoes: Optional[str] = None
    
    # Responsável
    nome_responsavel: Optional[str] = None
    cpf_responsavel: Optional[str] = None
    parentesco_responsavel: Optional[str] = None
    telefone_responsavel: Optional[str] = None
    email_responsavel: Optional[str] = None



# Enum para os motivos de desligamento
class MotivoDesligamentoEnum(str, Enum):
    FIM_CONTRATO = "Fim do Contrato"
    RESCISAO_ESTAGIARIO = "Rescisão pelo Estagiário"
    RESCISAO_EMPRESA = "Rescisão pela Empresa"
    OUTRO = "Outro"

# --- SCHEMAS PARA BENEFÍCIO ESTAGIÁRIO ---
class BeneficioEstagiarioSchema(BaseModel):
    valor_vale_alimentacao: float = Field(..., ge=0, description="Valor do Vale Alimentação")
    valor_vale_transporte: float = Field(..., ge=0, description="Valor do Vale Transporte")
    data_inicio_vigencia: date

    class Config:
        from_attributes = True

# --- SCHEMAS PARA CONTRATO ESTÁGIO ---
class ContratoEstagioSchema(BaseModel):
    estagiario_id: int
    lotacao_id: int
    supervisor_matricula: str
    classificacao_id: int
    beneficio_id: int
    numero_contrato: str
    data_assinatura: date
    data_inicio: date
    data_fim: date
    carga_horaria_diaria: int = Field(..., gt=0, le=24)
    horario: str
    observacoes: Optional[str] = None

    class Config:
        from_attributes = True

class DesligamentoContratoSchema(BaseModel):
    data_desligamento: date
    motivo_desligamento: MotivoDesligamentoEnum
    observacao_desligamento: Optional[str] = None

    
    

    
