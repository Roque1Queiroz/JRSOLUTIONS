#!/usr/bin/env bash
# ─────────────────────────────────────────────
#  SISTEMA GESTOR — Executor de suítes de teste
#
#  Roda, numa chamada só, as DUAS suítes:
#    A) deploy-cliente/test_pacote.py  -> valida o empacotador on-premise
#       (puro stdlib, desliga o plugin Django com -p no:django)
#    B) testes do Projeto (meigestao_app/*) com pytest-django
#       (precisa DJANGO_DEBUG=True porque o projeto não tem .env
#        e, em produção, o settings barra sem DJANGO_SECRET_KEY)
#
#  Uso:
#    bash scripts/executar_suites.sh [caminho_do_venv]
#  Exemplo:
#    bash scripts/executar_suites.sh /opt/data/.venvs/prod-audit-red
#
#  Retorna 0 se AMBAS passarem, 1 caso contrário.
# ─────────────────────────────────────────────
set -uo pipefail

# ── Caminhos ──
ROOT="$(cd "$(dirname "$0")/.." && pwd)"            # = deploy-cliente
SISTEMA="$(dirname "$ROOT")"                        # = o projeto do Sistema Gestor
VENV="${1:-/opt/data/.venvs/prod-audit-red}"
PYTEST="$VENV/bin/pytest"

PASS_A=1; PASS_B=1
echo "🧪 SISTEMA GESTOR — Executando as suítes de teste"
echo "──────────────────────────────────────────────"

if [ ! -x "$PYTEST" ]; then
  echo "❌ pytest não encontrado em: $PYTEST"
  echo "   Informe o venv como argumento, ex.: bash scripts/executar_suites.sh /caminho/do/venv"
  exit 1
fi

# ── Suíte A: empacotador on-premise (isolado) ──
echo ""
echo "► SUÍTE A: empacotador on-premise (deploy-cliente/test_pacote.py)"
if ( cd "$ROOT" && "$PYTEST" -q ); then
  PASS_A=0
  echo "   ↳ SUÍTE A: PASS ✓"
else
  echo "   ↳ SUÍTE A: FAIL ✗"
fi

# ── Suíte B: projeto Django ──
echo ""
echo "► SUÍTE B: testes do projeto (meigestao_app/*) com Django"
if ( cd "$SISTEMA" && DJANGO_DEBUG=True DB_TYPE=sqlite "$PYTEST" ); then
  PASS_B=0
  echo "   ↳ SUÍTE B: PASS ✓"
else
  echo "   ↳ SUÍTE B: FAIL ✗"
fi

# ── Resumo ──
echo ""
echo "══════════════════════════════════════════════"
echo " RESUMO:  A=$([ $PASS_A -eq 0 ] && echo PASS || echo FAIL)   B=$([ $PASS_B -eq 0 ] && echo PASS || echo FAIL)"
echo "══════════════════════════════════════════════"
if [ $PASS_A -eq 0 ] && [ $PASS_B -eq 0 ]; then
  echo "✅ TODAS as suítes passaram."
  exit 0
else
  echo "❌ Há falhas. Veja a saída acima para os detalhes."
  exit 1
fi
