#!/bin/bash

# Falha imediatamente se um comando falhar
set -e

echo "🚀 Iniciando ambiente do SISTEMA GESTOR..."

# 1. Aguardar o banco de dados (PostgreSQL) se estivermos usando um
if [ -n "$DB_HOST" ]; then
    DB_PORT="${DB_PORT:-5432}"
    DB_USER="${DB_USER:-postgres}"
    DB_NAME="${DB_NAME:-postgres}"

    echo "⌛ Aguardando PostgreSQL em ${DB_HOST}:${DB_PORT}..."
    until pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" >/dev/null 2>&1; do
      sleep 1
    done
    echo "✅ PostgreSQL pronto!"
fi

# 2. Executar migrações do banco de dados
echo "🔄 Aplicando migrações do Django..."
python manage.py migrate --noinput

# 3. Coletar arquivos estáticos para o WhiteNoise/Gunicorn
echo "📦 Coletando arquivos estáticos..."
python manage.py collectstatic --noinput --clear

# 4. Se um comando foi passado pelo container, repassa esse comando (ex.: worker Celery)
if [ "$#" -gt 0 ]; then
    echo "▶️ Executando comando customizado: $*"
    exec "$@"
fi

# 5. Iniciar o servidor (Gunicorn para Produção/SaaS, Runserver para Dev se for local)
# Se a variável DJANGO_DEBUG for False, usamos Gunicorn
if [ "$DJANGO_DEBUG" = "False" ]; then
    echo "🌐 Iniciando GUNICORN (Modo Produção/SaaS)..."
    exec gunicorn config.wsgi:application \
        --bind 0.0.0.0:8000 \
        --workers 3 \
        --timeout 120 \
        --access-logfile - \
        --error-logfile -
else
    echo "🛠️ Iniciando RUNSERVER (Modo Desenvolvimento/Local)..."
    exec python manage.py runserver 0.0.0.0:8000
fi
