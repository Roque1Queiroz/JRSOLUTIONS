#!/bin/bash
# entrypoint.sh do servico de chatbot
# - Aguarda o diretorio /data estar montado
# - Na primeira subida, indexa o MANUAL_EMBED_BOT.md se o Chroma estiver vazio
# - Sobe o uvicorn
# v2.5: avisa se a GROQ_API_KEY estiver vazia (sem abortar).
set -e

# v2.5: GROQ_API_KEY e opcional. Se faltar, o sobe e mostra mensagem
# amigavel; o /chat responde 503 quando perguntar (ver rag.py).
if [ -z "${GROQ_API_KEY:-}" ]; then
  echo "[chatbot] AVISO: GROQ_API_KEY nao definida no .env. O assistente"
  echo "         vai responder 503 ate voce preencher a chave."
  echo "         (veja README do pacote on-premise)"
fi

DATA_DIR="${CHATBOT_DATA_DIR:-/data}"
DB_DIR="${DATA_DIR}/db"
HIST_DIR="${DATA_DIR}/historico"
MANUAL_PATH="${DATA_DIR}/MANUAL_EMBED_BOT.md"

mkdir -p "${DB_DIR}" "${HIST_DIR}"

# Primeira-indexacao automatica do manual se o Chroma ainda nao existir
# e o MANUAL_EMBED_BOT.md estiver presente.
if [ ! -f "${DB_DIR}/chroma.sqlite3" ] && [ -f "${MANUAL_PATH}" ]; then
  echo "[chatbot] Primeira subida detectada. Indexando ${MANUAL_PATH} no Chroma..."
  # v2.7: o container NAO pode morrer se a indexacao falhar (ex.: sem internet
  # para baixar o modelo de embeddings do HuggingFace). Antes o `set -e`
  # derrubava o bot e o ERP recebia "assistente indisponivel" em vez do 503
  # explicativo. Falhou? Avisa, sobe o uvicorn e reindexa na proxima subida.
  if ! python - <<PY
from rag import process_and_index_document
with open("${MANUAL_PATH}", "rb") as f:
    process_and_index_document(f.read(), "MANUAL_EMBED_BOT.md")
print("[chatbot] Manual indexado com sucesso.")
PY
  then
    echo "[chatbot] AVISO: a indexacao do manual falhou (sem internet para"
    echo "         baixar o modelo de embeddings?). O bot vai subir, mas o"
    echo "         chat respondera 503 ate reiniciar o container com internet."
    echo "[chatbot] Continuando sem indice."
  fi
else
  echo "[chatbot] Chroma ja populado ou manual ausente. Pulando indexacao."
fi

exec "$@"
