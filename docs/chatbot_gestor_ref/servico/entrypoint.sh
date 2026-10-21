#!/bin/bash
# entrypoint.sh do servico de chatbot
# - Aguarda o diretorio /data estar montado
# - Na primeira subida, indexa o MANUAL_EMBED_BOT.md se o Chroma estiver vazio
# - Sobe o uvicorn
set -e

DATA_DIR="${CHATBOT_DATA_DIR:-/data}"
DB_DIR="${DATA_DIR}/db"
HIST_DIR="${DATA_DIR}/historico"
MANUAL_PATH="${DATA_DIR}/MANUAL_EMBED_BOT.md"

mkdir -p "${DB_DIR}" "${HIST_DIR}"

# Primeira-indexacao automatica do manual se o Chroma ainda nao existir
# e o MANUAL_EMBED_BOT.md estiver presente.
if [ ! -f "${DB_DIR}/chroma.sqlite3" ] && [ -f "${MANUAL_PATH}" ]; then
  echo "[chatbot] Primeira subida detectada. Indexando ${MANUAL_PATH} no Chroma..."
  python - <<PY
from rag import process_and_index_document
with open("${MANUAL_PATH}", "rb") as f:
    process_and_index_document(f.read(), "MANUAL_EMBED_BOT.md")
print("[chatbot] Manual indexado com sucesso.")
PY
else
  echo "[chatbot] Chroma ja populado ou manual ausente. Pulando indexacao."
fi

exec "$@"
