#!/usr/bin/env bash
# ─────────────────────────────────────────────
#  SISTEMA GESTOR — Patch de segurança para on-premise
#
#  Aplica (com backup) um patch MÍNIMO no settings.py
#  para permitir controlar SESSION_COOKIE_SECURE e
#  CSRF_COOKIE_SECURE pelo .env.
#
#  Por que: em produção (DEBUG=False) o settings original FORÇA
#  esses cookies como seguros. Em HTTPS isso é obrigatório e bom.
#  Mas numa instalação local por HTTP isso IMPEDE o login
#  (cookies "Secure" não são enviados via HTTP).
#
#  O default continua True, então a sua nuvem (HTTPS) permanece segura.
#
#  Uso: bash scripts/patch_seguranca.sh [caminho_do_settings.py]
# ─────────────────────────────────────────────
set -eo pipefail

SETTINGS="${1:-app/config/settings.py}"

if [ ! -f "$SETTINGS" ]; then
  echo "ℹ️  settings.py não encontrado em '$SETTINGS'. Nada a aplicar."
  exit 0
fi

if grep -q 'DJANGO_SESSION_COOKIE_SECURE' "$SETTINGS"; then
  echo "✅ settings.py já está configurado para on-premise. Ignorando."
  exit 0
fi

BAK="$SETTINGS.bak_$(date +%Y%m%d_%H%M%S)"
cp "$SETTINGS" "$BAK"
echo "🛟  Backup criado: $BAK"

# Torna as duas flags controláveis por env, mantendo o default True.
sed -i \
  -e 's/    SESSION_COOKIE_SECURE = True/    SESSION_COOKIE_SECURE = env.bool("DJANGO_SESSION_COOKIE_SECURE", default=True)/' \
  -e 's/    CSRF_COOKIE_SECURE = True/    CSRF_COOKIE_SECURE = env.bool("DJANGO_CSRF_COOKIE_SECURE", default=True)/' \
  "$SETTINGS"

echo "✅ Patch de segurança (on-premise HTTP) aplicado em $SETTINGS."
echo "   Default contínua True — a nuvem (HTTPS) permanece segura."
echo "   No .env do cliente você pode ligar False para rede local."
