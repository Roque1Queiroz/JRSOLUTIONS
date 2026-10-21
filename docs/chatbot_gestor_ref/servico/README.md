# Serviço de chatbot — Sistema Gestor (on-premise)

FastAPI + LangChain + ChromaDB + Groq. Atende em `/chat` (e `/health`, `/history`, `/upload`).

## Origem dos arquivos (transparência)

| Arquivo | Status | Observação |
|---|---|---|
| `main.py` | **Original** | Vem da VM (`/home/ubuntu/chatbot_gestor/main.py`). Tem os endpoints FastAPI. |
| `rag.py` | **Original** | Vem da VM. Lógica RAG com Groq + Chroma. |
| `database.py` | **RECONSTRUÍDO** | Original sumiu na faxina da VM em 2026-09-28. Reconstruído por Hermes a partir de dump de sessão. **Se você tiver o original, sobrescreva este arquivo.** |
| `models.py` | **RECONSTRUÍDO** | Mesma situação do `database.py`. |
| `requirements.txt` | **DERIVADO** | Extraído dos imports de `main.py` e `rag.py`. Versões pinadas para Python 3.11. |
| `Dockerfile` | **DERIVADO** | Imagem Python 3.11-slim + uvicorn. Sem segredo. |
| `entrypoint.sh` | **DERIVADO** | Primeira-subida indexa `MANUAL_EMBED_BOT.md` se Chroma vazio. |
| `MANUAL_EMBED_BOT.md` | **Original** | Manual do Sistema Gestor (626 linhas). Existe em `docs/MANUAL_EMBED_BOT.md` no repo. |

## O que este serviço FAZ

- Recebe `POST /chat` com `{session_id, message, empresa_dados?}`
- Persiste histórico em SQLite local (`chat_history.db`)
- Recupera contexto do ChromaDB (manual do Sistema Gestor)
- Responde com Groq (modelo `openai/gpt-oss-120b`)
- Retorna `{"answer": "..."}`

## O que este serviço NÃO FAZ

- **Não tem autenticação própria** — depende do Django (frontend). O proxy `/chatbot-api/` no Django é o que valida login.
- **Não expõe `/upload` publicamente** — só é acessível pela rede Docker interna.
- **Não roda offline** — precisa de internet (Groq é externo) e chave `GROQ_API_KEY`.

## Como rodar local (dev)

```bash
pip install -r requirements.txt
export GROQ_API_KEY=sua_chave
# indexar manual uma vez:
python -c "from rag import process_and_index_document; import os; \
    process_and_index_document(open('MANUAL_EMBED_BOT.md','rb').read(), 'MANUAL_EMBED_BOT.md')"
# subir:
uvicorn main:app --host 0.0.0.0 --port 8003
```

## Como rodar via Docker (on-premise)

O `deploy-cliente/docker-compose.yml` deste repo declara o serviço `chatbot`
na rede interna do Compose (sem `ports` no host). O Django (serviço `web`)
encaminha `/chatbot-api/*` para `http://chatbot:8003` (variável `CHATBOT_INTERNAL_URL`).

## Endpoint interno de teste

```bash
docker compose exec chatbot curl -s http://localhost:8003/health
# {"status":"ok"}
```

## Próximos passos (fora deste item)

- Multi-tenant com isolamento por empresa (atualmente o bot compartilha o Chroma entre todas as empresas no mesmo pacote).
- Bot offline (sem Groq). Não entra nesta leva.
- Reescrita como microsserviço agnóstico (separar conhecimento do ERP). Spec em `jrsolutions-services/`.
