# Atualização da VM — Relatório Financeiro Noturno (worker + beat)

Este guia cobre a aplicação, na VM da Oracle Cloud, dos dois últimos commits do
projeto em `Roque1Queiroz/Projeto-mei_gestao`:

- `e351665` — correção do wiring de deploy (entrypoint/worker) + fail-closed na task
- `a463c70` — relatório financeiro noturno (worker + beat) e exibição no dashboard

---

## 1. Garantir que `REDIS_URL` existe no `.env`

O broker do Celery (worker e beat) usa o Redis. Confira no `.env` da VM:

```env
REDIS_URL=redis://redis:6379/1
```

> Esse é o mesmo valor que o `settings.py` já usa como padrão, então nada mais
> precisa ser alterado se a variável já existir.

## 2. Puxar o código mais recente

```bash
cd <DIRETORIO_DO_PROJETO_NA_VM>

git pull origin main
```

## 3. Rodar as migrações (cria a tabela `RelatorioInteligencia`)

```bash
docker compose exec web python manage.py migrate
```

> Opcional (recomendado como checagem rápida):
> ```bash
> docker compose exec web python manage.py check
> ```

## 4. Recriar os containers com o novo serviço `beat`

O serviço `beat` é novo no `docker-compose.yml` e precisa ser criado. Também
recomenda-se recriar o `worker` para ele carregar a config de broker Redis:

```bash
docker compose up -d --build web worker beat
```

## 5. Confirmar que tudo subiu

```bash
docker compose ps
```

Você deve ver os containers:
- `mei_gestao_app`   (web / Gunicorn)
- `mei_gestao_worker`(celery -A config worker)
- `mei_gestao_beat`  (celery -A config beat)  ← NOVO

Acompanhe os logs para confirmar que o beat iniciou o agendamento:

```bash
docker compose logs -f beat
docker compose logs -f worker
```

No `beat`, deve aparecer o agendamento carregado (ex.: `bi-financeiro-noturno`,
diário às 00:00). No `worker`, ele deve consumir as tarefas da fila.

## 6. Comportamento esperado

1. **À meia-noite** (fuso `America/Sao_Paulo`), o `beat` dispara a task
   `processar_bi_financeiro_noturno`.
2. O **worker** executa e grava um `RelatorioInteligencia` por empresa com a
   análise (entradas, saídas, projeção, status SUCESSO/ALERTA/PERIGO).
3. Ao abrir o sistema, o **dashboard exibe** esse relatório do dia.
   - Se o relatório do dia ainda não existir (não rodou nem houve fallback), o
     dashboard **calcula na hora** como fallback, para nunca ficar sem dados.

---

## Troubleshooting rápido

| Sintoma | Possível causa / ação |
|---|---|
| Worker não consome fila | Broker não conectado ao Redis → confira `REDIS_URL` no `.env` e rode `docker compose up -d --build worker` |
| Tabela `RelatorioInteligencia` não existe | Migrações não aplicadas → `docker compose exec web python manage.py migrate` |
| Task lança erro se `RelatorioInteligencia` sumir | Comportamento **proposital** (fail-closed): sem o modelo, a task falha em vez de fingir sucesso |
| Beat não agenda | Serviço `beat` não subiu → `docker compose up -d beat` e confirme nos logs |
