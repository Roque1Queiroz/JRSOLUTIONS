# Integração do Chatbot (IA) — Sistema Gestor

Documento de referência da integração do assistente de IA (chatbot) com o
Sistema Gestor, e do que ainda falta aplicar na VM.

## Arquitetura (como o bot funciona)

- **Serviço separado (fora do Docker), no systemd** da VM Ubuntu:
  - Unit: `/etc/systemd/system/chatbot-gestor.service`
  - Descrição: API do Chatbot do Sistema Gestor
  - `User=ubuntu`, `WorkingDirectory=/home/ubuntu/chatbot_gestor`
  - `ExecStart=/home/ubuntu/chatbot_gestor/venv_chatbot/bin/python -m uvicorn main:app --host 0.0.0.0 --port 8003`
- **Stack:** FastAPI (`main.py`) + LangChain RAG + **ChromaDB** (`db/`, persist) +
  **Groq** (LLaMA 3.1 `llama-3.1-8b-instant`) + Hugging Face embeddings
  (`sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`).
- **Endpoints:**
  - `POST /upload` — recebe o manual (PDF ou MD) e indexa no ChromaDB (o "embed").
  - `POST /chat` — recebe `{session_id, message}` → responde `{answer}`.
  - `GET /history/{session_id}`, `GET /health`.
- **Frontend:** `templates/base.html` (Sistema Gestor) → `API_URL = ${protocol}//${hostname}:8003` (host-aware, porta 8003).
- **Conhecimento do bot:** documento indexado em `rag.py` via `process_and_index_document` (chunk 1000, overlap 400, `k=3`).

### Arquivos do bot (/home/ubuntu/chatbot_gestor)
- `main.py` — API FastAPI (`/upload`, `/chat`, `/health`)
- `rag.py` — embeddings/Chroma, chain RAG e **system prompt**
- `rag.py.backup`, `cli_chat.py`, `check_chroma.py`, `test_chatbot.py`
- `database.py`, `models.py` (SQLite `chat_history.db`)
- `.env` (Groq key), `db/` (ChromaDB), `widget_snippet.html`

## 1) Fazer o bot CORRIGIR a grafia do usuário (não replicar o erro)

Editar o `system_prompt` em `/home/ubuntu/chatbot_gestor/rag.py` e reiniciar.

```bash
cd /home/ubuntu/chatbot_gestor
python3 - <<'PY'
path = 'rag.py'
s = open(path, encoding='utf-8').read()
old = '"Se você não sabe a resposta, diga que não sabe. Responda sempre em Português do Brasil.\\n\\n"'
new = ('"Se você não sabe a resposta, diga que não sabe. Responda sempre em Português do Brasil. "\n'
       '"Sempre corrija erros de digitação ou ortografia do usuário e responda usando a grafia correta — nunca repita palavras escritas errado. "\n'
       '"Ajude apenas dúvidas sobre o Sistema Gestor (acesso, vendas, estoque, financeiro, fiscal, almoxarifado, produção, O.S., compras, relatórios e planos).\\n\\n"')
assert old in s, 'TEXTO NAO ENCONTRADO - verificar arquivo atual'
open(path, 'w', encoding='utf-8').write(s.replace(old, new, 1))
print('OK: prompt atualizado')
PY

sudo systemctl restart chatbot-gestor
sudo systemctl status chatbot-gestor --no-pager
```

## 2) Re-embedar o manual atualizado (planos, FAQ, glossário, admin)

O manual novo está no repositório em `docs/MANUAL_EMBED_BOT.md` (~626 linhas).
Trazer para a VM (se o repo for privado, copiar do clone existente do Sistema
Gestor na VM) e re-indexar:

```bash
cd /home/ubuntu/chatbot_gestor
curl -sL -o MANUAL_EMBED_BOT.md https://raw.githubusercontent.com/Roque1Queiroz/Projeto-mei_gestao/main/docs/MANUAL_EMBED_BOT.md
wc -l MANUAL_EMBED_BOT.md          # deve ser ~626

# re-indexa o manual no ChromaDB:
curl -s -X POST http://127.0.0.1:8003/upload -F "file=@MANUAL_EMBED_BOT.md"
```

## 3) Testar

```bash
# palavra errada (bot deve corrigir e não replicar):
curl -s -X POST http://127.0.0.1:8003/chat \
  -H 'Content-Type: application/json' \
  -d '{"session_id":"t_grafia","message":"como cadastru um clinete nvoe?"}'

# melhorias (planos):
curl -s -X POST http://127.0.0.1:8003/chat \
  -H 'Content-Type: application/json' \
  -d '{"session_id":"t_planos","message":"em quais planos aparece o chat de IA?"}'
```

## Observações

- A regra de grafia também consta em `docs/jrsolutions-local-ai-bridge.md`
  (SYSTEM_PROMPT de exemplo) e na seção "Comportamento do assistente" do
  `MANUAL_EMBED_BOT.md`.
- **Segurança:** a `GROQ_API_KEY` (em `/home/ubuntu/chatbot_gestor/.env`) foi
  exposta num chat; **gerar nova chave no console da Groq** e atualizar o `.env`,
  depois `sudo systemctl restart chatbot-gestor`.
