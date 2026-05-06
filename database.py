from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
import os

# ===============================
# DATABASE CONFIGURATION
# ===============================
# 📌 Suporta variáveis de ambiente para maior segurança
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres.pvmlhnqrnhciuqyzwnuj:fcsllessVEooGkbu@aws-1-us-west-2.pooler.supabase.com:6543/postgres"
)

# 🔐 SSL obrigatório no Supabase
# pool_pre_ping evita conexões mortas (importante no Render)
engine = create_engine(
    DATABASE_URL,
    connect_args={"sslmode": "require"},
    pool_pre_ping=True,
    pool_recycle=3600,  # Recicla conexões a cada hora
    echo=False  # Mude para True para debug (loga queries SQL)
)

# ===============================
# SESSION FACTORY
# ===============================
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# ===============================
# BASE DECLARATIVA
# ===============================
Base = declarative_base()


# ===============================
# DEPENDENCY INJECTION
# ===============================
def get_db() -> Session:
    """
    Dependency injection para FastAPI
    
    Fornece uma sessão do banco de dados que é automaticamente
    fechada após o uso.
    
    Yield:
        Session: Sessão SQLAlchemy do banco de dados
    
    Example:
        @app.get("/items")
        def get_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Inicializa o banco de dados criando todas as tabelas
    
    Deve ser chamado na primeira inicialização da aplicação
    """
    Base.metadata.create_all(bind=engine)
