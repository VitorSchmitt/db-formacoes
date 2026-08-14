import os
import shutil
from datetime import datetime
from fastapi import UploadFile, HTTPException


def salvar_arquivo_rede(
    arquivo: UploadFile,
    pasta_base: str,
    nome_arquivo: str
):

    if not arquivo.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Somente arquivos PDF são permitidos."
        )

    ano_atual = datetime.now().year

    pasta_ano = os.path.join(
        pasta_base,
        str(ano_atual)
    )

    print(">>> ANTES DO MAKEDIRS")

    try:
        os.makedirs(pasta_ano, exist_ok=True)
        print(">>> DEPOIS DO MAKEDIRS")
        print(">>> EXISTE:", os.path.exists(pasta_ano))
    except Exception as e:
        print(">>> ERRO NO MAKEDIRS:", repr(e))
        raise

    

    caminho_arquivo = os.path.join(
        pasta_ano,
        nome_arquivo
    )

    print("========================================")
    print("PASTA BASE:", pasta_base)
    print("PASTA ANO:", pasta_ano)

    try:

        print(">>> CAMINHO DO ARQUIVO:", caminho_arquivo)
        print(">>> ANTES DO OPEN")
        
        with open(caminho_arquivo, "wb") as f:
            shutil.copyfileobj(
                arquivo.file,
                f
            )
        
        print(">>> DEPOIS DO OPEN")
        print(">>> ARQUIVO EXISTE:", os.path.isfile(caminho_arquivo))
        
        if os.path.isfile(caminho_arquivo):
            print(">>> TAMANHO:", os.path.getsize(caminho_arquivo))

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Erro ao salvar arquivo: {str(e)}"
        )

    return os.path.join(
        str(ano_atual),
        nome_arquivo
    ).replace("\\", "/")
