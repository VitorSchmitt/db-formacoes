from pydantic import BaseModel, EmailStr,ConfigDict, field_validator, field_serializer
from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from estagiario.enums import SexoEnum
from estagiario.enums import MotivoDesligamentoEnum

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




# ===============================
# BENEFÍCIO ESTAGIÁRIO
# ===============================


# USAR NO POST: Garante que os dados obrigatórios do banco venham na requisição
class BeneficioEstagiarioCreate(BaseModel):
    valor_vale_alimentacao: float
    valor_vale_transporte: float
    data_inicio_vigencia: date

# USAR NO PUT: Segue o padrão solicitado com campos opcionais para atualização
class BeneficioEstagiarioUpdate(BaseModel):
    valor_vale_alimentacao: Optional[float] = None
    valor_vale_transporte: Optional[float] = None
    data_inicio_vigencia: Optional[date] = None


# ===============================
# CONTRATO  ESTAGIÁRIO
# ===============================
# Usado no POST de criação
class ContratoEstagioCreate(BaseModel):
    estagiario_id: int
    lotacao_id: int
    supervisor_matricula: str
    classificacao_id: int    
    numero_contrato: str
    data_assinatura: date
    data_inicio: date
    data_fim: date
    carga_horaria_diaria: int
    horario: str
    vale_alimentacao: bool
    quantidade_vale_transporte: int
    observacoes: Optional[str] = None

# Usado no PUT de edição
class ContratoEstagioUpdate(BaseModel):
    estagiario_id: Optional[int] = None
    lotacao_id: Optional[int] = None
    supervisor_matricula: Optional[str] = None
    classificacao_id: Optional[int] = None    
    numero_contrato: Optional[str] = None
    data_assinatura: Optional[date] = None
    data_inicio: Optional[date] = None
    data_fim: Optional[date] = None
    carga_horaria_diaria: Optional[int] = None
    horario: Optional[str] = None
    vale_alimentacao:Optional[bool]= None
    quantidade_vale_transporte:Optional[int] = None
    observacoes: Optional[str] = None

# Usado especificamente na rota de desligamento
class DesligamentoContratoInput(BaseModel):
    data_desligamento: date
    motivo_desligamento: MotivoDesligamentoEnum
    observacao_desligamento: Optional[str] = None




class FrequenciaEstagioBase(BaseModel):
    contrato_id: int
    competencia: date
    dias: int
    horas_realizadas: Decimal
    observacao: Optional[str] = None

    # 1. Transforma "MM/YYYY" recebido do Frontend em um date (ex: "07/2026" -> 2026-07-01)
    @field_validator("competencia", mode="before")
    @classmethod
    def transformar_string_em_data(cls, v):
        if isinstance(v, str):
            try:
                # Tenta converter o formato MM/YYYY definindo o dia automaticamente como 01
                return datetime.strptime(v, "%m/%Y").date()
            except ValueError:
                try:
                    # Mantém o suporte caso mandem o formato completo YYYY-MM-DD
                    return datetime.strptime(v, "%Y-%m-%d").date()
                except ValueError:
                    raise ValueError("A competência deve estar no formato MM/YYYY ou YYYY-MM-DD")
        return v

    # 2. Transforma o date do banco em "MM/YYYY" ao enviar para o Frontend
    @field_serializer("competencia")
    def formatar_data_para_frontend(self, v: date) -> str:
        return v.strftime("%m/%Y")


class FrequenciaEstagioCreate(FrequenciaEstagioBase):
    pass


class FrequenciaEstagioUpdate(BaseModel):
    contrato_id: Optional[int] = None
    competencia: Optional[date] = None
    dias: Optional[int] = None
    horas_realizadas: Optional[Decimal] = None
    observacao: Optional[str] = None

    # Aplica a mesma lógica de entrada no Update, se a competência for enviada
    @field_validator("competencia", mode="before")
    @classmethod
    def transformar_string_em_data(cls, v):
        if isinstance(v, str):
            try:
                return datetime.strptime(v, "%m/%Y").date()
            except ValueError:
                return datetime.strptime(v, "%Y-%m-%d").date()
        return v


class FrequenciaEstagioResponse(FrequenciaEstagioBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
    
    

    
