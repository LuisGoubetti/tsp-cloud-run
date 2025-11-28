# Dockerfile
FROM python:3.10-slim

WORKDIR /app

# Copia os arquivos de dependência e instala
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código da aplicação
COPY main.py .

# A porta padrão no Cloud Run é a 8080
ENV PORT 8080

# Comando para rodar o servidor Gunicorn (que executa o Flask)
CMD exec gunicorn --bind :$PORT --workers 1 main:app