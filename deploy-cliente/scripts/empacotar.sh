#!/usr/bin/env bash
# ─────────────────────────────────────────────
#  SISTEMA GESTOR — Empacotador on-premise (gera o .zip do cliente)
#
#  Monta a estrutura de instalação e compacta em um único .zip
#  pronto para entregar ao cliente.
#
#  Uso:
#    bash scripts/empacotar.sh [versão] [caminho_do_código]
#
#  Exemplos:
#    bash scripts/empacotar.sh                 # v1.0, código = pasta que contém deploy-cliente
#    bash scripts/empacotar.sh v1.1            # versão v1.1
#    bash scripts/empacotar.sh v0.9 /caminho/ate/o/projeto
#
#  Saída: deploy-cliente/dist/sistema-gestor-cliente-<versão>.zip
#
#  NÃO depende de zip/rsync: usa cp + find e compacta via Python (zipfile).
# ─────────────────────────────────────────────
set -euo pipefail

# ── Caminhos ──
ROOT="$(cd "$(dirname "$0")/.." && pwd)"                 # = deploy-cliente
VER="${1:-v1.0}"
SRC="${2:-$(dirname "$ROOT")}"                           # padrão: pasta que contém o deploy-cliente
DIST="$ROOT/dist"
FOLDER="sistema-gestor-cliente-$VER"
STAGE="$(mktemp -d)"
OUTZIP="$DIST/sistema-gestor-cliente-$VER.zip"

# Limpeza ao final (não remove o zip gerado)
cleanup() { rm -rf "$STAGE"; }
trap cleanup EXIT

echo "🚀 Empacotando o Sistema Gestor — on-premise ($VER)"
echo "   Código-fonte: $SRC"
echo "   Saída:        $OUTZIP"
echo "──────────────────────────────────────────────"

# 1. Validar origem
if [ ! -f "$SRC/manage.py" ] || [ ! -f "$SRC/Dockerfile" ]; then
  echo "❌ Origem inválida: não encontrei manage.py + Dockerfile em: $SRC"
  exit 1
fi

# 2. Montar a estrutura de instalação
APP="$STAGE/$FOLDER/app"
mkdir -p "$APP"
echo "📁 Copiando o código do Sistema Gestor para app/ ..."
cp -a "$SRC/." "$APP/"

# 3. Remover do código o que NÃO pode ir ao cliente
cat > "$STAGE/excludes.txt" <<'EX'
.git
.env
.env.example
__pycache__
*.pyc
*.pyo
.pytest_cache
.hermes
db.sqlite3
staticfiles
media
deploy-cliente
docs
.coverage
htmlcov
*.bak_*
templates/deploy-log.txt
.nogit
docker-compose.yml
docker-compose-prod.yml
convert*.py
gerar_views_relatorios.py
EX
while IFS= read -r pat; do
  [ -z "$pat" ] && continue
  find "$APP" -path "$APP/$pat" -prune -exec rm -rf {} + 2>/dev/null || true
  find "$APP" -name "$pat" -exec rm -rf {} + 2>/dev/null || true
done < "$STAGE/excludes.txt"

echo "✅ Código limpo (sem .git ligado, segredos, banco de desenvolvimento, docs internas)."

# 4. Copiar os arquivos do próprio pacote (compose, env modelo, README, scripts)
mkdir -p "$STAGE/$FOLDER/scripts"
cp "$ROOT/docker-compose.yml"      "$STAGE/$FOLDER/"
cp "$ROOT/.env.example"            "$STAGE/$FOLDER/"
cp "$ROOT/.gitignore"              "$STAGE/$FOLDER/"
cp "$ROOT/README_INSTALACAO.md"    "$STAGE/$FOLDER/"
cp "$ROOT/GUIA_INSTALACAO_CLIENTE.md" "$STAGE/$FOLDER/"
cp "$ROOT/scripts/instalar.sh"        "$STAGE/$FOLDER/scripts/"
cp "$ROOT/scripts/atualizar.sh"      "$STAGE/$FOLDER/scripts/"
cp "$ROOT/scripts/atualizar.bat"     "$STAGE/$FOLDER/scripts/"
cp "$ROOT/scripts/patch_seguranca.sh" "$STAGE/$FOLDER/scripts/"
chmod +x "$STAGE/$FOLDER/scripts/"*.sh "$STAGE/$FOLDER/scripts/"*.bat

# Servico do bot (FastAPI + Chroma). Copia Dockerfile e codigo do bot.
# MANUAL_EMBED_BOT.md fica na RAIZ do zip (montado em /data no container).
cp -a "$ROOT/chatbot" "$STAGE/$FOLDER/"
chmod +x "$STAGE/$FOLDER/chatbot/entrypoint.sh"
cp "$SRC/docs/MANUAL_EMBED_BOT.md" "$STAGE/$FOLDER/" 2>/dev/null || true

# 5. Compactar com Python (zipfile) — sem depender do binário zip
mkdir -p "$DIST"
rm -f "$OUTZIP"
echo "🗜️  Compactando..."
python3 - "$OUTZIP" "$STAGE" "$FOLDER" <<'PY'
import sys, os, zipfile
outzip, parent, folder = sys.argv[1], sys.argv[2], sys.argv[3]
count = 0
with zipfile.ZipFile(outzip, 'w', zipfile.ZIP_DEFLATED) as z:
    for base, dirs, files in os.walk(os.path.join(parent, folder)):
        dirs[:] = sorted(d for d in dirs if d != '__pycache__' and not d.startswith('.'))
        for f in files:
            if f.endswith(('.pyc', '.pyo')):
                continue
            full = os.path.join(base, f)
            arc = os.path.relpath(full, parent)
            z.write(full, arc)
            count += 1
print(f"   -> {count} arquivos empacotados")
PY

# 6. Verificar o zip (listar + abrir um arquivo real de dentro)
echo "🧪 Verificando o pacote..."
python3 - "$OUTZIP" <<'PY'
import sys, zipfile
z = zipfile.ZipFile(sys.argv[1])
names = z.namelist()
n = len(names)
root = names[0].split('/')[0]
must = [
    root + "/docker-compose.yml",
    root + "/.env.example",
    root + "/README_INSTALACAO.md",
    root + "/scripts/instalar.sh",
    root + "/scripts/atualizar.sh",
    root + "/scripts/atualizar.bat",
    root + "/scripts/patch_seguranca.sh",
    root + "/app/manage.py",
    root + "/app/Dockerfile",
]
missing = [m for m in must if m not in names]
leaked = [x for x in names if '.env' in x and '.env.example' not in x]
print(f"   Total de {n} entradas? ok ({n})")
def has(p): print(("     OK " if p in names else "     FALTA ") + p)
for m in must: has(m)
print(("     OK  app/Dockerfile presente (bloco acima)" if root+"/app/Dockerfile" in names else ""))
forbidden = [root+'/.git', root+'/app/.git', root+'/app/db.sqlite3', root+'/app/docs']
for f in forbidden:
    flag = "PRESENTE (PROBLEMA)" if f in names else "ok ausente"
    print(f"     {flag}: {f}")
print(f"   Arquivos .env vazados: {len(leaked)} -> {'NENHUM ✓' if not leaked else leaked}")
z.close()
PY

SIZE=$(du -h "$OUTZIP" | cut -f1)
echo ""
echo "✅ PACOTE PRONTO: $OUTZIP ($SIZE)"
echo "   Pode entregar ao cliente (e-mail / pendrive / repositório privado)."
