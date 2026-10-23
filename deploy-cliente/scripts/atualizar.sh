#!/usr/bin/env bash
# ─────────────────────────────────────────────
#  SISTEMA GESTOR — Atualização on-premise (Linux/macOS)
#
#  O QUE FAZ (4 passos, do mais cuidadoso para o mais rápido):
#    1. Backup do banco PostgreSQL (dados do cliente)
#    2. Backup do .env (defesa contra alteração)
#    3. Sobe a nova versão (rebuild + up)
#    4. Aplica as migrations
#
#  COMO USAR:
#    1. Coloque a pasta 'app/' NOVA (vinda do sistema-gestor-cliente-vX.zip)
#       junto deste script, na MESMA pasta onde estão docker-compose.yml e .env
#    2. Rode: bash scripts/atualizar.sh
#    3. Aguarde e teste em http://localhost:8000
#
#  O QUE NÃO MUDA:
#    - .env (chaves, senhas, GROQ_API_KEY)
#    - Volumes Docker (db_data, media, staticfiles)
#    - Empresas, usuários, cadastros, ordens de serviço
#
#  Requisitos: Docker + plugin "docker compose".
# ─────────────────────────────────────────────
set -euo pipefail

# Sempre rodar a partir da raiz do pacote (deploy-cliente/)
cd "$(dirname "$0")/.."

echo "═══════════════════════════════════════════"
echo "  SISTEMA GESTOR — Atualização"
echo "═══════════════════════════════════════════"
echo

# Pré-requisitos
command -v docker >/dev/null 2>&1 || { echo "❌ Docker não instalado."; exit 1; }
docker compose version >/dev/null 2>&1 || { echo "❌ Plugin 'docker compose' indisponível."; exit 1; }

if [ ! -f app/manage.py ]; then
  echo "❌ Pasta app/ com o código novo não encontrada."
  echo "   Coloque a pasta app/ desta versão junto deste script"
  echo "   (extraia do sistema-gestor-cliente-vX.zip)."
  exit 1
fi

# 1. Backup do banco
echo "[1/4] Fazendo backup do banco..."
DATA=$(date +%Y%m%d)
BAK="backup_${DATA}.sql"
if docker compose exec -T db pg_dump -U gestor gestor > "$BAK" 2>/dev/null; then
  echo "       Backup salvo em: $BAK"
else
  echo "       AVISO: backup não foi possível. Continuando mesmo assim..."
fi
echo

# 2. Backup do .env (defesa)
echo "[2/4] Protegendo o .env..."
if [ -f .env ]; then
  cp -f .env .env.bak
  echo "       Cópia de segurança em .env.bak"
else
  echo "❌ .env não encontrado. Rode primeiro: bash scripts/instalar.sh"
  exit 1
fi
echo

# 3. Subir a nova versão
echo "[3/4] Atualizando o sistema (pode demorar alguns minutos)..."
docker compose up -d --build
echo

# 4. Aplicar migrations
echo "[4/4] Aplicando atualizações do banco..."
docker compose exec web python manage.py migrate --noinput
echo

echo "═══════════════════════════════════════════"
echo "  PRONTO! Acesse: http://localhost:8000"
echo "═══════════════════════════════════════════"
echo
echo "  Se algo deu errado, o backup do banco está em: $BAK"
echo "  Para reverter: copie o app/ antigo de volta e rode este script de novo."