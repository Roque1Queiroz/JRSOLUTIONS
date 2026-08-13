# Estágio 1: Build das Dependências
FROM python:3.11-slim as builder

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Instala dependências do sistema necessárias para compilar algumas libs Python
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Cria e ativa ambiente virtual para isolar dependências
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt


# Estágio 2: Runtime Final
FROM python:3.11-slim

WORKDIR /app

# Instala apenas bibliotecas de runtime essenciais (como libpq para o PostgreSQL)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    gettext \
    && rm -rf /var/lib/apt/lists/*

# Copia o ambiente virtual do estágio anterior
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copia o código do projeto
COPY . .

# Garante permissões de execução para scripts
RUN chmod +x /app/scripts/*.sh || true

# Porta padrão do Django/Gunicorn
EXPOSE 8000

# O Entrypoint gerencia migrações e prepara o ambiente antes de subir o sistema
ENTRYPOINT ["/app/scripts/entrypoint.sh"]
