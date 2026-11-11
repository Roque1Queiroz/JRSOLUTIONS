# SPEC v2.5 — Pacote on-premise instalável de verdade

Status: rascunho em revisão (2026-10-24)
Autor: Rocão (a partir do diagnóstico do pacote v2.4.1 na VM)

## Motivo

O pacote on-premise v2.4.1 (entregue em 23/10) **nunca instalou do zero**.
O teste na VM (containers `gestor_cliente_*`) provou isso: web, worker e beat
entram em loop de reinicialização com `exit 127` e o log repetindo:

```
bash: /app/scripts/entrypoint.sh: No such file or directory
```

Não é problema do cliente. São **8 defeitos no próprio pacote**, todos
reproduzíveis e todos corrigíveis sem tocar no código de negócio do ERP.

O objetivo da v2.5 é: **um `sistema-gestor-cliente-v2.5.zip` que, extraído em
uma máquina limpa com Docker, sobe de verdade** — banco Postgres, web no ar,
chat respondendo, sem intervention manual do José.

## Fora de escopo

- Nenhuma mudança de regra de negócio do ERP.
- Nenhuma mudança no painel/UX.
- Nenhuma feature nova da fila de atualizações.

## Diagnóstico (evidência)

| # | Defeito | Evidência | Impacto |
|---|---|---|---|
| D1 | `ENTRYPOINT ["/app/scripts/entrypoint.sh"]` sem `bash` | `Dockerfile:52`; o `.zip` grava `app/scripts/entrypoint.sh` como `-rw-rw-r--` (sem bit de execução) e o compose monta `./app:/app` por bind mount | **P0** — container não sobe: `permission denied` / `No such file` |
| D2 | `.env.example` do pacote não tem `DB_TYPE` | `deploy-cliente/.env.example` tem `DB_NAME/DB_USER/DB_PASSWORD/DB_HOST/DB_PORT` e **nenhum** `DB_TYPE` | **P0** — `settings.py:11` tem default `sqlite` → o app ignora o Postgres do compose e usa SQLite local |
| D3 | `settings.py` usa `env.db()`, que só lê `DATABASE_URL` | `config/settings.py:209`; teste: `env.db()` → `ImproperlyConfigured: Set the DATABASE_URL environment variable` | **P0** — mesmo com `DB_TYPE=postgres`, o banco não conecta (o compose e o `.env` só fornecem `DB_*`) |
| D4 | `web`, `worker` e `beat` rodam `migrate` ao mesmo tempo | `scripts/entrypoint.sh:25` roda `migrate` sempre; o entrypoint é comum aos 3 serviços e não há flag | **P1** — corrida de migrations (lock/contention) |
| D5 | `GROQ_API_KEY=${GROQ_API_KEY:?...}` no compose | `deploy-cliente/docker-compose.yml:114` — o `:?` **aborta o `docker compose up` inteiro** se a chave estiver vazia | **P1** — cliente sem Groq (ou ainda sem preencher o `.env`) não sobe nada |
| D6 | Serviço do bot usa import relativo com arquivos achatados | `deploy-cliente/chatbot/main.py:11` faz `from .database import ...`; o `Dockerfile` do bot copia tudo em `/app` (sem `__init__.py`) e roda `uvicorn main:app` | **P0** — `ImportError: attempted relative import with no known parent package` |
| D7 | `pandas` e `plotly` no `requirements.txt`, sem uso no código | `requirements.txt:46-47`; `grep` não acha import em `meigestao_app/` | **P1** — build lento e frágil (já falhou no Python 3.13) |
| D8 | `MANUAL_EMBED_BOT.md` existe em 2 lugares no zip | raiz e `chatbot/` | **P2** — duplicata; o compose monta `./MANUAL_EMBED_BOT.md` |

## Critérios de aceite

### CA1 — O container sobe sem depender do bit de execução
Extrair o `.zip` em disco, com o `entrypoint.sh` sem bit `+x`, e subir o
`web`: o container **não** pode falhar com `permission denied` nem
`No such file or directory`.

- Teste: `deploy-cliente/test_pacote.py::test_zip_entrypoint_roda_sem_bit_exec`
  — o `Dockerfile` do `app/` dentro do zip tem
  `ENTRYPOINT ["bash", "/app/scripts/entrypoint.sh"]`.
- Teste: `test_zip_entrypoint_tem_modo_exec_ou_roda_via_bash` — o
  `entrypoint.sh` no zip tem bit de execução **ou** é invocado via `bash`.

### CA2 — O app usa o Postgres que o compose provisiona
Com `DB_TYPE=postgres` e as variáveis `DB_*` presentes, o Django deve
apontar para o Postgres do compose — **sem** `DATABASE_URL` e **sem**
`ImproperlyConfigured`.

- Teste: `meigestao_app/core/test_pacote_onpremise_db.py::test_db_postgres`
  — carrega `config.settings` com `DB_TYPE=postgres` + `DB_*` e sem
  `DATABASE_URL`; o `ENGINE` precisa ser `django.db.backends.postgresql`,
  `NAME` == `DB_NAME`, `HOST` == `DB_HOST`, `PORT` == `DB_PORT`.

### CA3 — O `.env.example` do pacote declara `DB_TYPE=postgres`
O pacote provisiona Postgres; o modelo de `.env` precisa pedir Postgres.

- Teste: `test_pacote.py::test_env_example_declara_db_type_postgres` — o
  `.env.example` do pacote contém `DB_TYPE=postgres`.

### CA4 — Só o `web` aplica migrations
`worker` e `beat` **não** podem rodar `migrate`.

- Teste: `test_pacote.py::test_somente_web_roda_migrations` — o
  `scripts/entrypoint.sh` (que vai no `app/`) tem o gate
  `RUN_MIGRATIONS`; o `docker-compose.yml` define `RUN_MIGRATIONS=true`
  **apenas** no serviço `web`.

### CA5 — Cliente sem chave Groq ainda sobe o sistema
`docker compose up` **não** pode abortar por `GROQ_API_KEY` vazia.

- Teste: `test_pacote.py::test_chatbot_nao_derruba_o_compose_sem_groq` — o
  compose não usa `${GROQ_API_KEY:?...}`; usa `${GROQ_API_KEY:-}`.
- Teste: `test_pacote.py::test_chatbot_explica_groq_vazio_no_log` — o
  `entrypoint.sh` do bot avisa quando a chave falta, sem `exit 1`.

### CA6 — O serviço do bot sobe (import relativo resolvido)
O bot precisa ser importável no layout do container.

- Teste: `meigestao_app/core/test_chatbot_onpremise_fonte.py` (novo CA) —
  os módulos do bot no pacote (`deploy-cliente/chatbot/`) importam sem
  `ImportError` quando executados no layout do container (arquivos em
  `/app`, `uvicorn main:app`).

### CA7 — Build do `app/` não instala pandas/plotly
Dependências pesadas e não usadas ficam fora.

- Teste: `test_pacote.py::test_requirements_sem_pandas_plotly` — o
  `requirements.txt` que vai no `app/` não contém `pandas` nem `plotly`.

### CA8 — `MANUAL_EMBED_BOT.md` aparece uma vez só
- Teste: `test_pacote.py::test_manual_embot_aparece_uma_vez` — no zip há
  exatamente uma cópia do manual (na raiz, onde o compose monta).

## Plano de teste

Os CAs de pacote (CA1, CA3, CA4, CA5, CA7, CA8) ficam em
`deploy-cliente/test_pacote.py` (Suíte A, stdlib puro).
Os CAs de código (CA2, CA6) ficam em
`meigestao_app/core/test_pacote_onpremise_db.py` e
`meigestao_app/core/test_chatbot_onpremise_fonte.py` (Suíte B, Django).

## Verificação extra (fora do pytest)

- `docker compose config` na VM com `.env` real → precisa passar.
- Subir o pacote v2.5 do zero na VM → `web` healthy, `/entrar/` HTTP 200,
  banco Postgres com as tabelas do Django, bot `/health` respondendo.
- `bash -n` em todos os scripts.

## Risco

O `settings.py` é compartilhado com a nuvem (SQLite). A correção do CA2
troca `env.db()` por um dict montado a partir de `DB_*` — o comportamento
na nuvem **não muda**, porque a nuvem também usa `DB_TYPE=sqlite`.
O gate `RUN_MIGRATIONS` é opt-in: sem a flag, o entrypoint não migra
(nuvem continua com `DB_TYPE=sqlite` e precisa do gate ligado — conferir
no compose da nuvem antes de subir).

> **Ponto de atenção:** o `docker-compose.yml` da **nuvem** (na VM,
> `/home/ubuntu/Sistema_Gestor`) também usa o mesmo `entrypoint.sh`. Se
> passarmos a exigir `RUN_MIGRATIONS=true` para migrar, a nuvem para de
> migrar. Decisão: manter o default do entrypoint como **migrar** quando
> `RUN_MIGRATIONS` não está definido, e usar `RUN_MIGRATIONS=false` no
> `worker`/`beat` do pacote. Assim a nuvem não muda e o pacote para de
> duplicar migration.
