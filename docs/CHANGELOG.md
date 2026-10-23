# Changelog — Sistema Gestor

Anotações curtas por versão. A versão viva está em `meigestao_app/__init__.py`
quando existir. O pacote pronto para cliente fica em
`deploy-cliente/dist/sistema-gestor-cliente-<versão>.zip`.

## v2.4.1 — 2026-10-22

Mesmo conteúdo da v2.4 + **scripts de atualização** oficiais no pacote.

**Mudanças:**

- `deploy-cliente/scripts/atualizar.bat` — atualizador Windows (duplo
  clique). Faz backup do banco (`backup_AAAAMMDD.sql`), backup do `.env`
  (`.env.bak`), sobe a nova versão e aplica migrations.
- `deploy-cliente/scripts/atualizar.sh` — equivalente para Linux/macOS.
- `empacotar.sh` — passa a incluir os dois scripts no zip e na lista
  de arquivos obrigatórios.
- `README_INSTALACAO.md` — descreve o fluxo de update.

**Por que este patch:**

O script anterior vivia só na base `life` (`atualizar.bat`),
não era parte do projeto. Agora o caminho de atualização é oficial,
versionado, e o empacotador garante que vai no zip.

**Como o cliente atualiza:**

1. Recebe o `sistema-gestor-cliente-v2.4.1.zip`.
2. Extrai **só a pasta `app/`** por cima da antiga (não sobrescreve
   `.env` nem os volumes Docker).
3. Duplo clique em `scripts/atualizar.bat` (Windows) ou
   `bash scripts/atualizar.sh` (Linux/macOS).

**Para o cliente que já estava na v2.4:**

Mesma coisa — só extrair `app/` novo e rodar o atualizar. O `.env`
existente, a chave Groq e todos os dados ficam intactos.

---

## v2.4 — 2026-10-22

Pacote on-premise com os **4 itens da fila** fechados. Baseado no push
noturno `Roque1Queiroz/JRSOLUTIONS` (commit `6a947cd`).

**Itens fechados:**

- **Item 1 — Nosso boleto** (conta parcelada). 8/8 CA verdes em
  `meigestao_app/financeiro/test_nosso_boleto.py`.
- **Item 2 — Etiqueta limpa da peça**. 5/5 CA verdes em
  `meigestao_app/almoxarifado/test_etiqueta_limpa_peca.py`.
- **Item 3 — Código do cliente por empresa**. 6/6 CA verdes em
  `meigestao_app/clientes/test_codigo_cliente.py`.
- **Item 4 — Bot no pacote on-premise**. 9/9 CA verdes:
  - 2/2 `meigestao_app/core/test_chatbot_proxy.py` (proxy Django
    `/chatbot-api/chat` → `http://chatbot:8003`, sem expor a porta).
  - 4/4 `meigestao_app/core/test_chatbot_onpremise_zip.py`
    (empacotador exclui `.env` real, mantém `.env.example`).
  - 3/3 `meigestao_app/core/test_chatbot_onpremise_fonte.py`
    (serviço do bot tem `Dockerfile`, `main.py`, `rag.py`,
    `database.py`, `models.py`, `requirements.txt`, `entrypoint.sh`,
    `MANUAL_EMBED_BOT.md`, `README.md`).

**Infra / qualidade:**

- 104 testes passam em `meigestao_app/core/` (sem regressão).
- 3 testes em `deploy-cliente/test_pacote.py` passam (estrutura do zip,
  sem `.env` real, sem segredos).
- Autenticação GitHub via **SSH** (`/opt/data/workspace/.ssh-gh/id_ed25519`)
  — PAT fine-grained deu 4 tipos diferentes de 403 antes disso ser
  decidido.

**Empilhamento de mudanças com a v2.3:**

- Spec do Item 4 marcada como **implementado** em `docs/SPECS/bot-on-premise.md`.
- Fila `docs/SPECS/FILA-ATUALIZACOES.md` com o Item 4 em verde.
- Branch `backup-pre-push-20261022-2351` no `projeto-correcao` (ponto
  de retorno se algo der errado).

**Verificações para o cliente:**

```
sha256: 19bfb80439dcb5e2f36c54c51d8aad930a5753ee7a50cc3111acc002d2f1e83e
tamanho: 2.5 MB
arquivos: 386
```

Antes de instalar, o cliente deve:

1. Preencher `GROQ_API_KEY` no `.env.example` (renomear para `.env`).
2. Conferir que `CHATBOT_INTERNAL_URL=http://chatbot:8003` está como
   o empacotador deixou.
3. Rodar `bash scripts/instalar.sh`.

---

## v2.3 — 2026-10-21 (resumo)

Versão anterior. Mantida no repositório para clientes que ainda não
atualizaram.