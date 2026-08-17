import os
from supabase import create_client

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

print("========================================")
print("SUPABASE_URL:", SUPABASE_URL)
print("SUPABASE_KEY configurada:", bool(SUPABASE_KEY))
print("========================================")

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)

resultado = supabase.storage.from_("contratos").list()

print("CONEXÃO COM STORAGE OK")
print("ARQUIVOS:", resultado)
