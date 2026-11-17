#!/usr/bin/env bash
# ─────────────────────────────────────────────
#  SISTEMA GESTOR — Instalador on-premise
#  Rode na máquina do cliente:  bash scripts/instalar.sh
#  Requisitos: Docker + plugin "docker compose".
# ─────────────────────────────────────────────
set -euo pipefail

# Sempre rodar a partir da raiz do pacote (deploy-cliente/)
cd "$(dirname "$0")/.."

echo "🚀 SISTEMA GESTOR — Instalação on-premise"
echo "──────────────────────────────────────────────"

# 1. Pré-requisitos
if ! command -v docker >/dev/null 2>&1; then
  echo "❌ Docker não instalado. Instale antes de continuar:"
  echo "   https://docs.docker.com/engine/install/"
  exit 1
fi
if ! docker compose version >/dev/null 2>&1; then
  echo "❌ Plugin 'docker compose' indisponível. Atualize o Docker."
  echo "   (Versões antigas usam 'docker-compose' — troque no final do script.)"
  exit 1
fi

# 2. Garante o código em ./app (deve conter manage.py + Dockerfile)
if [ ! -f app/manage.py ] || [ ! -f app/Dockerfile ]; then
  echo "❌ Pasta 'app/' incompleta."
  echo "   Coloque aqui o código do Sistema Gestor (mantendo a estrutura do projeto)."
  exit 1
fi

# 3. Aplica o patch de segurança para HTTP local (com backup automático)
bash scripts/patch_seguranca.sh app/config/settings.py || true

# 4. Gera o .env automaticamente se ainda não existir
if [ ! -f .env ]; then
  if [ ! -f .env.example ]; then
    echo "❌ .env.example não encontrado. Isto é certo?"
    exit 1
  fi
  SECRET=$(openssl rand -base64 48 | tr -d '\n')
  DB_PASS=$(openssl rand -base64 24 | tr -d '\n')
  IP=$(hostname -I 2>/dev/null | awk '{print $1}' || true)

  cp .env.example .env
  sed -i "s|^DJANGO_SECRET_KEY=.*|DJANGO_SECRET_KEY=${SECRET}|" .env
  sed -i "s|^DB_PASSWORD=.*|DB_PASSWORD=${DB_PASS}|" .env
  if [ -n "${IP:-}" ]; then
    sed -i "s|IP_DO_SERVIDOR|${IP}|g" .env
  fi
  echo "✅ .env criado automaticamente (chave e senha do banco geradas)."
else
  echo "ℹ️  Já existe .env — mantendo as configurações atuais."
fi

APP_PORT=$(grep '^APP_PORT=' .env | cut -d= -f2 || echo 8000)

# 5. Constrói e sobe
echo "🔨 Construindo as imagens (a primeira vez demora alguns minutos)..."
docker compose up -d --build

echo ""
echo "✅ SISTEMA NO AR!"
IP=$(hostname -I 2>/dev/null | awk '{print $1}' || echo "localhost")
echo "   Acesse de outro computador:  http://${IP}:${APP_PORT}"
echo "   Acesse nesta máquina:        http://localhost:${APP_PORT}"
echo ""
echo "   ➜ Criar o administrador:"
echo "        docker compose exec web python manage.py createsuperuser"
echo ""
echo "   ➜ Ver os logs (Ctrl+C para sair):"
echo "        docker compose logs -f web"
echo ""
echo "   ── CREDENCIAIS GERADAS (anote, não aparecem de novo) ──"
grep -E '^(DB_USER|DB_PASSWORD)=' .env | sed 's/^/       /'
echo "   ──────────────────────────────────────────────────────────"
