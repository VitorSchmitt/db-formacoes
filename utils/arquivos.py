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

    os.makedirs(
        pasta_ano,
        exist_ok=True
    )

    print("========================================")
    print("PASTA BASE:", pasta_base)
    print("ANO:", ano_atual)
    print("PASTA ANO:", pasta_ano)
    print("========================================")

    caminho_arquivo = os.path.join(
        pasta_ano,
        nome_arquivo
    )

    try:

        with open(caminho_arquivo, "wb") as f:

            shutil.copyfileobj(
                arquivo.file,
                f
            )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Erro ao salvar arquivo: {str(e)}"
        )

    return os.path.join(
        str(ano_atual),
        nome_arquivo
    ).replace("\\", "/")
