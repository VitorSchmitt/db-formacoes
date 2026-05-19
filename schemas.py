from pydantic import BaseModel
from datetime import date
from typing import Optional


# ===============================
# FORMAÇÃO
# ===============================
class FormacaoBase(BaseModel):
    descricao: str
    data_termino: Optional[date] = None
    carga_horaria: Optional[int] = None
    modalidade: Optional[str] = None

    data_inicio: Optional[date] = None
    periodo: Optional[str] = None
    publico_alvo: Optional[str] = None
    investimento: Optional[float] = None
    meta_participantes: Optional[int] = 0
    plano_id: Optional[int] = None


class FormacaoCreate(FormacaoBase):
    pass


class FormacaoUpdate(BaseModel):
    descricao: Optional[str] = None
    data_inicio: Optional[date] = None
    data_termino: Optional[date] = None
    periodo: Optional[str] = None
    carga_horaria: Optional[int] = None
    modalidade: Optional[str] = None
    publico_alvo: Optional[str] = None
    investimento: Optional[float] = None
    meta_participantes: Optional[int] = None
    plano_id: Optional[int] = None
# ===============================
# SERVIDOR
# ===============================
class ServidorCreate(BaseModel):
    matricula: str
    nome: str
    cargo_id: int

class ServidorUpdate(BaseModel):
    nome: str
    cargo_id: int

class UsuarioCreate(BaseModel):
    username: str
    senha: str
    perfil: str
