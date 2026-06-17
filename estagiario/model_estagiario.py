class Estagiario(Base):
    __tablename__ = "estagiarios"

    id = Column(Integer, primary_key=True)

    nome = Column(String(200), nullable=False)

    cpf = Column(
        String(14),
        unique=True,
        nullable=False
    )

    data_nascimento = Column(Date)

    email = Column(String(200))

    telefone = Column(String(30))

    endereco = Column(Text)

    instituicao_ensino = Column(String(200))

    curso = Column(String(200))

    semestre = Column(String(20))

    ativo = Column(
        Boolean,
        default=True,
        nullable=False
    )

    observacoes = Column(Text)

    # Responsável
    nome_responsavel = Column(String(200))

    cpf_responsavel = Column(String(14))

    parentesco_responsavel = Column(String(50))

    telefone_responsavel = Column(String(30))

    email_responsavel = Column(String(200))

    contratos = relationship(
        "ContratoEstagio",
        back_populates="estagiario",
        cascade="all, delete-orphan"
    )
