# Spec — Painel Executivo em Modo Demonstração (público)

| Campo | Valor |
|---|---|
| **Versão** | 0.1 (rascunho p/ revisão) |
| **Status** | implementado (08/2026) |
| **Autor** | José Roque / Hermes |
| **Data** | 2026-08-22 |
| **Módulos afetados** | core, relatorios, landing |
| **Plano** | todos (ferramenta de vendas) |

---

## 1. Objetivo (por quê?)
Dar ao prospect um **painel executivo de demonstração** acessível SEM login, com dados realistas
de exemplo, para ele **experimentar o poder do sistema antes de comprar** — botão "Ver demonstração"
na landing leva até ele; ao final, CTA para o cadastro (30 dias grátis). É o "carro-chefe de vendas".

## 2. Contexto atual
- Já existe **DashboardView** (core) com KPIs + gráfico de faturamento (USUÁRIO logado, dados reais).
- Já existe **Painel BI** (`/relatorios/bi/`) + **DRE em PDF** (logado).
- **Não existe** painel público/demonstração com dados de exemplo. A landing mostra só texto/preços.
- Precisão: insumi que NÃO há rota `/demo/` nem seed de dados de exemplo. (a confirmar na revisão)

## 3. Escopo
- **Incluído:**
  - Rota pública **`/demo/`** (e link da landing). Acessível com e sem login.
  - **Dados de exemplo realistas** (empresa fictícia "Empresa Demonstração ME"): vendas, clientes,
    estoque, financeiro carregados num **ambiente isolado de demonstração** (nunca dados de usuários reais).
  - Painel executivo novo: **KPIs** (faturamento do mês, ticket médio, saldo, estoque baixo, clientes novos),
    **gráfico de faturamento** (comparativo mensal), **top produtos**, **vendas recentes**, **DRE resumido**.
  - **CTA** no fim: "Criar conta e testar os 30 dias grátis" → `/cadastro/`.
  - Marca d'água/aviso **"Demonstração com dados de exemplo"**.
- **Excluído (não-escopo):** NÃO alterar os painéis de usuário real; NÃO criar tenant de verdade;
  NÃO permitir salvar/alterar nos dados de demo; NÃO expor dados reais de qualquer empresa.

## 4. Requisitos Funcionais (RF)
- RF1 — Visitante anônimo acessa `GET /demo/` → vê o painel executivo preenchido com dados de exemplo.
- RF2 — Usuário logado também acessa `/demo/` (reuso para vendedor mostrar).
- RF3 — O painel mostra: KPIs (faturamento do mês, ticket médio, saldo de caixa, estoque baixo,
       clientes novos), gráfico comparativo de faturamento (6 meses), top 5 produtos, últimas vendas,
       resumo DRE (receitas/despesas/lucro).
- RF4 — Botão de CTA → `/cadastro/`.
- RF5 — Aviso visível "🧪 Demonstração — dados fictícios de exemplo".
- RF6 — A landing ganha um botão **"Ver demonstração"** → `/demo/`.

## 5. Requisitos Não-Funcionais
- Rápido (dados leves/em memória ou empresa fixa); leitura apenas (GET).
- Seguro: `/demo/` **nunca** consulta dados reais de usuários; só a empresa de exemplo.
- Responsivo (mobile OK), mesmo padrão visual do sistema.
- Não exige login, não grava nada.

## 6. Dados / Modelo
- **Seed de demonstração idempotente** cria (ou reusa) a empresa fictícia de CNPJ fixo
  (ex.: `00.000.000/0001-DEMO`) + usuário técnico + dados de exemplo (vendas recentes e de meses passados
  p/ o comparativo, clientes, produtos, estoque, contas/transações). Rodável via `manage.py shell`/management command.
- Nenhum campo novo no modelo. O painel lê os mesmos modelos, filtrados pela empresa demo.

## 7. Fluxo / Telas
- Landing → botão **"Ver demonstração"** → `/demo/` → painel executivo (KPIs + gráfico + DRE) → CTA → `/cadastro/`.
- Rota nova: `demo/` em `config/urls.py` (view `demo_dashboard` no `core`).
- Template novo: `templates/meigestao_app/core/demo_dashboard.html` (estilo do sistema, sem login).

## 8. Segurança / Restrições
- `/demo/` é **públido, só-leitura, empresa fixa demo** — protegido de consultar dados reais por construção.
- Multi-tenant: o painel demo filtra SEMPRE pela empresa demo (nunca por `request.user`).

## 9. Critérios de Aceite (TESTES — o "check")
- CA1 — `GET /demo/` anônimo → **200** e contém "Demonstração" + KPIs.
- CA2 — `/demo/` **não** expõe nome/data de nenhuma empresa real.
- CA3 — Seed idempotente: rodar 2x não duplica a empresa demo.
- CA4 — Painel mostra faturamento do mês > 0 (dados de exemplo).
- CA5 — Botão CTA aponta para `/cadastro/`.
- CA6 — Suíte completa continua verde (pytest).

## 10. Riscos / Dependências
- Risco: seed de exemplo misturar com dados reais → mitigado pela empresa fixa/isolada e filtro fixo.
- Dependência: verificação (`pytest` + `hermes verify`) e deploy na VM com backup.

---

## Fluxo
1. ✅ Spec escrita (este arquivo).
2. ⏳ **Revisão** (José + Hermes) — confirmar escopo/não-escopo e critérios.
3. ⏳ Implementar com TDD (branch `feature/demo-dashboard`).
4. ⏳ `pytest` (critérios de aceite) + `hermes verify --json`.
5. ⏳ Deploy na VM (backup) → validar ao vivo.
6. ⏳ Fechar spec (status `implementado`).
