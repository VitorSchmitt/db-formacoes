from pydantic import BaseModel
from datetime import date
from typing import Optional


# ===============================
# FORMAÇÃO
# ===============================

class FormacaoBase(BaseModel):
    descricao: str

    data_inicio: Optional[date] = None
    data_termino: Optional[date] = None
    periodo: Optional[str] = None

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
    periodo: Optional[str] = None

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
