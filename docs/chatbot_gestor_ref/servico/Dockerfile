# Dockerfile do servico de chatbot (Sistema Gestor — on-premise)
# Imagem leve com Python 3.11 slim para manter o download pequeno.
# O ChromaDB persiste em /data/db e o manual vai em /data/MANUAL_EMBED_BOT.md,
# ambos compartilhados com o host via volume no docker-compose.

FROM python:3.11-slim

# Evita bytecode e buffering do stdout/stderr (logs aparecem em tempo real)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Diretorio de trabalho
WORKDIR /app

# Dependencias primeiro (cache de camadas)
COPY requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

# Codigo do servico (main, rag, database, models)
COPY main.py rag.py database.py models.py /app/

# Dados persistentes (db/ chroma, manual, historico sqlite)
# Montados via volume pelo docker-compose, nao copiados na imagem.
RUN mkdir -p /data/db /data/historico
VOLUME ["/data"]

# Porta interna do bot — JAMAIS publicada no host (rede Docker so).
EXPOSE 8003

# Entrypoint: sobe uvicorn escutando em todas as interfaces da rede Docker
ENTRYPOINT ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8003"]
