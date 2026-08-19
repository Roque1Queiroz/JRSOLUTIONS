# Fix Chatbot 19/08/2026 — Indexação ChromaDB acumulava conteúdo antigo

## Sintoma (reportado/verificado)
O bot respondia informação **desatualizada** sobre planos:
- Dizia "chat de IA apenas nos planos Profissional e Enterprise" (errado).
- Dizia "não sei o número de usuários por plano" mesmo com o manual correto.

O `MANUAL_EMBED_BOT.md` (disco, local e VM) estava **correto** (mesmo checksum
`e161fd62…`): "chat de IA em TODOS os planos, Básico: 2 usuários, PME: 5, Enterprise: 20".

## Causa raiz (2 problemas)
1. **Acúmulo de chunks** — `rag.py::process_and_index_document` usa
   `Chroma.from_documents(...)`, que **só ADICIONA** quando a pasta de persistência
   já existe. O manual foi indexado 3x (28 → 87 → 147 chunks), acumulando chunks
   antigos com o texto errado. A busca RAG podia puxar o chunk velho.
2. **`k` muito baixo** — retriever `search_kwargs={"k": 3}` não recuperava o chunk
   numérico dos planos (estava na posição ~4/40), então o LLM respondia "não sei".

## Correções aplicadas na VM (idempotentes, com backup)
1. **Limpar + re-indexar uma vez**: backup `db.bak_20260819_230740`, apagou `db/`,
   parou+iniciou o serviço, re-indexou via `POST /upload`. Resultado: **147 → 60 chunks**,
   **0 chunks** com o texto errado ("não é exibido").
2. **Patch `rag.py`** (`patch_rag_reindex_limpo.py` → backup `rag.py.bak_reindex`):
   antes de `Chroma.from_documents`, **limpa a coleção** (`_collection.delete(ids)`
   de todos os ids qualificados). Agora re-indexar NÃO acumula mais (idempotente).
   Verificado: re-indexar 2x seguidas mantém 60 chunks.
3. **`k: 3 → 5`** (backup `rag.py.bak_k`): retriever passa a recuperar o chunk
   numérico dos planos. Básico=2, PME=5, Enterprise=20 agora respondidos.

## Testes após o fix (na VM)
- "em quais planos o assistente de IA está disponível?" → **todos os planos, incl. Básico** ✅
- "quantos usuários o plano Básico permite?" → **2** ✅
- "quantos usuários permite o plano Profissional?" → **5** ✅
- "como incluo um produto no estoque?" → passo a passo ✅
- "como emtir uma nota fisçal?" → corrige grafia + passo a passo ✅

## Como aplicar o mesmo fix numa instalação futura (on-premise)
O patch precisa apenas das 3 etapas acima no `rag.py` e do re-embed:
```bash
# 1) patch de limpeza na re-indexação  (ver patch_rag_reindex_limpo.py)
cp rag.py rag.py.bak_reindex
python3 patch_rag_reindex_limpo.py      # injeta limpeza antes do Chroma.from_documents
# 2) subir o k para 5
python3 -c "
s=open('rag.py').read()
s=s.replace('search_kwargs={\"k\": 3}', 'search_kwargs={\"k\": 5}', 1)
open('rag.py','w').write(s)"
# 3) limpar e re-indexar uma vez
systemctl stop chatbot-gestor
rm -rf db && mkdir db
systemctl start chatbot-gestor
curl -s -X POST http://127.0.0.1:8003/upload -F "file=@MANUAL_EMBED_BOT.md"
```
> **Lição:** o multi-tenant/on-premise deve entregar o `rag.py` já com a limpeza
> idempotente embutida, para nunca mais acumular conteúdo de versões antigas.

## Arquivos de backup na VM
- `/home/ubuntu/chatbot_gestor/db.bak_20260819_230740` (índice antigo, 147 chunks)
- `/home/ubuntu/chatbot_gestor/rag.py.bak_reindex` (antes do patch de limpeza)
- `/home/ubuntu/chatbot_gestor/rag.py.bak_k` (antes do ajuste k=5)

## Status
- Serviço `chatbot-gestor`: **active**
- `/health` → `{"status":"ok"}`
- Índice limpo e idempotente (60 chunks)
