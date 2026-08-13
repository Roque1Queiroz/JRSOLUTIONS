#!/bin/bash

# Falha imediatamente se um comando falhar
set -e

echo "🚀 Iniciando ambiente do SISTEMA GESTOR..."

# 1. Aguardar o banco de dados (PostgreSQL) se estivermos usando um
if [ "$DB_HOST" != "" ]; then
    echo "⌛ Aguardando banco de dados ($DB_HOST)..."
    while ! curl -s http://$DB_HOST:5432 > /dev/null; do
      # Nota: Usamos o comando 'timeout' do sistema para não esperar infinitamente
      sleep 1
    done
    echo "✅ Banco de dados detectado!"
fi

# 2. Executar migrações do banco de dados
echo "🔄 Aplicando migrações do Django..."
python manage.py migrate --noinput

# 3. Coletar arquivos estáticos para o WhiteNoise/Gunicorn
echo "📦 Coletando arquivos estáticos..."
python manage.py collectstatic --noinput --clear

# 4. Iniciar o servidor (Gunicorn para Produção/SaaS, Runserver para Dev se for local)
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
