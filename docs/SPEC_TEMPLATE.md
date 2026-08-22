# Spec — <Título da funcionalidade>

> Modelo de **Spec-Driven Development** (Engineering com Agentes Inteligentes — cap. 6).
> Preencha ANTES de gerar código. A IA (Hermes) implementa contra esta spec; o check
> (`pytest`/`hermes verify`) só "entrega" o que passa nos critérios de aceite.

| Campo | Valor |
|---|---|
| **Versão** | 0.1 |
| **Status** | rascunho / em revisão / aprovado / implementado |
| **Autor** | José Roque |
| **Data** | YYYY-MM-DD |
| **Módulos afetados** | core / vendas / estoque / financeiro / ... |
| **Plano** | básico / profissional / enterprise / todos |

---

## 1. Objetivo (por que?)
Em 1–3 frases: o problema que esta funcionalidade resolve e para quem.

## 2. Contexto / Cenário atual
O que existe hoje (limitações, dor). Nada de invenção: baseado no sistema real.

## 3. Escopo
- **Incluído:**
- **Excluído (não-escopo):** (importante para evitar "a IA inventa extra")

## 4. Requisitos Funcionais (o que o sistema FAZ)
- RF1 — (Como usuário [papel], eu [ação], para [resultado]).
- RF2 — ...

## 5. Requisitos Não-Funcionais (qualidade/segurança)
- Performance, segurança (RBAC/multi-tenant), LGPD, usabilidade.

## 6. Dados / Modelo
- Novos campos/tabelas (ou alterações). Regras de negócio e validações.

## 7. Fluxo / Telas
- Passo a passo do uso (entrada → saída). URLs/rotas previstas.

## 8. Segurança / Restrições por Plano e Empresa
- Isolamento multi-tenant; permissões; limite por plano; trial expirado.

## 9. Critérios de Aceite (TESTES — o "check")
- CA1 — [ação] → resultado esperado (vira teste automatizado).
- CA2 — ...
> A função só estará completa quando os critérios passarem (pytest + hermes verify).

## 10. Riscos / Dependências
- Riscos, integrações (ex.: Asaas, IA/Groq), migração/backup.

---

## Fluxo de trabalho (Spec → Implementa → Verifica)
1. **Escrever a spec** (este arquivo, num branch `feature/xxxx`).
2. **Revisar** comigo (Hermes): clareza, critérios de aceite testáveis, não-escopo.
3. **Implementar** (IA com método + TDD) contra a spec.
4. **Verificar**: `pytest` (critérios de aceite viram testes) + `hermes verify --json`.
5. **Deploy** (VM) com backup → **validar ao vivo**.
6. **Fechar** a spec (status `implementado`) e arquivar.
