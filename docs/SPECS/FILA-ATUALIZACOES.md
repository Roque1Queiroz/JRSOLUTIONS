# Fila de atualizações — Sistema Gestor

Itens com spec fechada. Entram na próxima versão quando José mandar executar. Não implementar só porque estão nesta lista.

| # | Item | Spec | Status | Desde |
|---|---|---|---|---|
| 1 | Nosso boleto (conta parcelada) | [nosso-boleto-parcelas.md](nosso-boleto-parcelas.md) | em produção 2026-11-11 | 2026-10-09 |
| 2 | Etiqueta limpa da peça (QR) | [etiqueta-limpa-peca.md](etiqueta-limpa-peca.md) | em produção 2026-11-11 | 2026-10-09 |
| 3 | Código do cliente por empresa | [codigo-cliente.md](codigo-cliente.md) | em produção 2026-11-11 | 2026-10-10 |
| 4 | Bot no pacote on-premise | [bot-on-premise.md](bot-on-premise.md) | em produção 2026-11-11 (rota raiz /chatbot-api/chat) | 2026-10-10 |

## Ainda não entram nesta fila

- Pacote de textos do admin: lista ainda aberta (2 itens anotados).
- Nota discreta no lembrete: jeito combinado, spec não fechada.

## Registro de deploy — 2026-11-11 (produção)

A VM já tinha o schema da "leva v25" (migrações `clientes.0002_leva_v25`,
`clientes.0003_sequencia_codigo`, `financeiro.0010_leva_v25` aplicadas em 2026-10-20).
Faltava o código. Subido nesta data:

- `almoxarifado/peca_views.py` + `peca_view.html` — saldo com ponto decimal (item 2).
- `almoxarifado/views.py` — peças da central de etiquetas ordenadas por SKU.
- `central_etiquetas.html` — sem a classe `label-print-surface` (etiqueta limpa).
- `clientes/models.py` — lock por empresa na geração do código (item 3).
- `core/views.py` + `core/urls.py` + `config/urls.py` — proxy do bot e rota RAIZ
  `/chatbot-api/chat` (item 4; no on-premise não há nginx para reescrever o path).
- `config/settings.py` — `CHATBOT_INTERNAL_URL`, WAL/timeout do SQLite, engine Postgres por `DB_*`.
- `security: financeiro.0011` — só `verbose_name`/`related_name` (nenhuma mudança de schema).

Verificação: 340 testes verdes; rotas testadas logado em produção (`/`, `/clientes/`,
`/clientes/criar/` com código 1, `/financeiro/parcelas/`, `/financeiro/parcelas/nova/`,
boleto, `/almoxarifado/etiquetas/`, `/almoxarifado/peca/<sku>/`, `/chatbot-api/chat`).
Backup pré-deploy: `/home/ubuntu/backups_predeploy/sistema_gestor_predeploy_20261111_233142.tar.gz`.
