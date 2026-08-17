import os
from fastapi import UploadFile, HTTPException
from supabase import create_client


SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)


def salvar_arquivo_rede(
    arquivo: UploadFile,
    pasta_base: str,
    nome_arquivo: str
):

    # ==========================================
    # VALIDAÇÃO DO ARQUIVO
    # ==========================================

    if not arquivo.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Somente arquivos PDF são permitidos."
        )

    # ==========================================
    # ANO ATUAL
    # ==========================================

    from datetime import datetime

    ano_atual = datetime.now().year

    # ==========================================
    # CAMINHO NO SUPABASE STORAGE
    # ==========================================

    caminho_arquivo = (
        f"{ano_atual}/{nome_arquivo}"
    )

    try:

        # Volta o arquivo para o início
        arquivo.file.seek(0)

        # Lê o PDF
        conteudo = arquivo.file.read()

        if not conteudo:
            raise HTTPException(
                status_code=400,
                detail="O arquivo PDF está vazio."
            )

        # ==========================================
        # UPLOAD PARA SUPABASE STORAGE
        # ==========================================

        resultado = (
            supabase
            .storage
            .from_("contratos")
            .upload(
                caminho_arquivo,
                conteudo,
                {
                    "content-type": "application/pdf",
                    "upsert": "true"
                }
            )
        )

        print("========================================")
        print(">>> UPLOAD SUPABASE REALIZADO")
        print(">>> BUCKET: contratos")
        print(">>> CAMINHO:", caminho_arquivo)
        print(">>> TAMANHO:", len(conteudo))
        print(">>> RESULTADO:", resultado)
        print("========================================")

    except HTTPException:
        raise

    except Exception as e:

        print(">>> ERRO NO UPLOAD SUPABASE:", repr(e))

        raise HTTPException(
            status_code=500,
            detail=f"Erro ao salvar arquivo no Supabase: {str(e)}"
        )

    # ==========================================
    # RETORNA O CAMINHO QUE SERÁ SALVO NO BANCO
    # ==========================================

    return caminho_arquivo
