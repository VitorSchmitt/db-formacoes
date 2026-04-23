# Imagem base estável
FROM python:3.11-slim

# Diretório de trabalho
WORKDIR /app

# Copia arquivos
COPY . .

# Instala dependências
RUN pip install --no-cache-dir -r requirements.txt

# Porta
EXPOSE 10000

# Comando de execução
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]
