# Arquitetura do Sistema - MEI Gestão

Este documento descreve as decisões técnicas, a stack tecnológica e a organização estrutural do projeto MEI Gestão.

## 🛠️ Stack Tecnológica

| Componente | Ferrramenta | Justificativa |
|---|---|---|
| **Linguagem** | Python 3.x | Ecossistema maduro para gestão e manipulação de dados. |
| **Framework Web** | Django 4.2+ | "Batteries included" — oferece Admin, Auth e ORM integrados de alta qualidade. |
| **Banco de Dados** | SQLite | Ideal para MEI (Microempreendedor Individual), fácil backup e zero latência de rede. |
| **Frontend UI** | Bootstrap 5 | Padrão de mercado para interfaces administrativas responsivas. |
| **Visualização** | Chart.js 4+ | Performance superior e customização nativa via JS para Dashboards. |
| **Infra Local** | Docker Compose | Padronização de ambiente para evitar o "funciona na minha máquina". |

## 🏗️ Estrutura do Projeto

O projeto é dividido em aplicativos Django especializados (Modular Monolith):

- `core`: Hub central, Dashboard e gerenciamento da entidade "Empresa".
- `vendas`: Lógica de transações comerciais, itens de venda e fluxos de pedido.
- `clientes`: CRM básico (Cadastro, busca e histórico de relacionamento).
- `estoque`: Controle de produtos, SKUs e níveis críticos de estoque.
- `financeiro`: Fluxo de caixa de entradas e saídas e sistema de reembolsos.
- `fiscal`: Geração e controle de Notas Fiscais.
- `usuarios`: Gestão de permissões e perfis de acesso.

## 🚢 Ambiente Docker

O projeto utiliza Docker para garantir consistência.

- **Porta Principal**: 8000
- **Volumes**: O arquivo `db.sqlite3` é persistido em um volume nomeado para evitar perda de dados.
- **Variáveis de Ambiente**: Puxadas de um arquivo `.env` (não versionado).

## 🛡️ Decisões de Design (Higher Mind)

1. **Theme First**: Consumo de variáveis CSS nativas (`:root`) para suporte real a Dark/Light mode sem re-render.
2. **Editorial Typography**: Uso da fonte "Inter" em escala modular para maximizar a escaneabilidade de dados financeiros.
3. **Resilience Engineering**: Transações atômicas obrigatórias em fluxos que envolvem múltiplos modelos (ex: Venda + Itens).
4. **Agent-First Ready**: A estrutura de pastas e API foi pensada para fácil integração futura com agentes de IA.
