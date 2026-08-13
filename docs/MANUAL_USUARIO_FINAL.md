# 📘 MANUAL DO USUÁRIO — SISTEMA GESTOR (PME/SaaS)

**Versão:** 1.0 — Maio/2026  
**Desenvolvido por:** JR Solutions Tecnologia  
**Público-alvo:** Usuário final (operadores, vendedores, gerentes e administradores)

---

## Sumário

1. [Introdução](#1-introdução)
2. [Acesso ao Sistema (Login)](#2-acesso-ao-sistema)
3. [Painel Principal (Dashboard)](#3-painel-principal)
4. [Gestão de Clientes](#4-gestão-de-clientes)
5. [Gestão de Vendas](#5-gestão-de-vendas)
6. [Gestão de Produtos e Estoque](#6-gestão-de-produtos-e-estoque)
7. [Gestão Financeira](#7-gestão-financeira)
8. [Gestão Fiscal (Notas Fiscais)](#8-gestão-fiscal)
9. [Gestão de Almoxarifado](#9-gestão-de-almoxarifado)
10. [Gestão de Produção (PCP)](#10-gestão-de-produção)
11. [Ordens de Serviço (O.S.)](#11-ordens-de-serviço)
12. [Gestão de Compras](#12-gestão-de-compras)
13. [BI e Relatórios](#13-bi-e-relatórios)
14. [Lembretes e Anotações](#14-lembretes-e-anotações)
15. [Personalização (White Label)](#15-personalização-white-label)
16. [Configurações e Administração](#16-configurações-e-administração)
17. [Perguntas Frequentes (FAQ)](#17-perguntas-frequentes)

---

## 1. Introdução

O **SISTEMA GESTOR** é uma plataforma completa de gestão empresarial desenvolvida para Pequenas e Médias Empresas (PMEs). Ele integra em um único sistema:

- Cadastro de clientes
- Controle de vendas e orçamentos
- Gerenciamento de estoque e produtos
- Controle financeiro (receitas, despesas e reembolsos)
- Emissão e controle de notas fiscais
- Almoxarifado com endereçamento por prateleira
- Planejamento e controle de produção (PCP)
- Ordens de serviço
- Gestão de compras e fornecedores
- Relatórios gerenciais e BI

### Perfis de Usuário

| Perfil | Descrição |
|---|---|
| **Administrador** | Acesso total a todos os módulos e configurações |
| **Gerente** | Acesso a relatórios, aprovações e visão geral |
| **Vendedor** | Acesso a clientes, vendas e consulta de estoque |
| **Operador** | Acesso a produção, serviços e movimentações |
| **Almoxarife** | Acesso exclusivo ao módulo de Almoxarifado |

### Navegação Geral

O sistema possui uma **barra lateral (sidebar)** à esquerda com os menus organizados por seção:

- **Menu Principal:** Visão Geral (Dashboard) e BI de Resultados
- **Gestão Comercial:** Clientes e Vendas
- **Gestão de Estoque:** Produtos e Almoxarifado
- **Gestão Operacional:** Produção (PCP), Ordens de Serviço e Compras
- **Gestão Financeira:** Caixa, Receitas e Reembolsos
- **Gestão Fiscal:** Notas Fiscais
- **Configurações:** Acesso ao painel administrativo

No canto superior direito você encontra:
- 🔔 **Notificações** — alerta de reembolsos pendentes
- 🌙 **Alternar Tema** — troca entre modo claro e escuro
- 👤 **Menu do Usuário** — personalizar marca, ajustes e sair

> **Dica:** Em dispositivos móveis (celular/tablet), toque no ícone ☰ para abrir o menu lateral.

---

## 2. Acesso ao Sistema

O sistema utiliza a tela de autenticação administrativa do Django para o login.

### Como acessar

1. Abra o navegador e acesse o endereço fornecido pelo administrador (ex: `http://seuservidor:8000`).
2. Se você **não estiver logado**, o sistema redirecionará automaticamente para a tela de login, localizada em `/admin/login/`.
3. Na tela de login, preencha:
   - **Usuário** — o nome de usuário fornecido pelo administrador
   - **Senha** — sua senha pessoal
4. Clique em **Iniciar sessão**.
5. Após o login, você será redirecionado para o **Painel Principal (Dashboard)**.

> **Importante:** Usuários com perfil "Almoxarife" são redirecionados automaticamente para o Dashboard do Almoxarifado ao invés do Dashboard geral.

### Primeiro Acesso

No primeiro acesso, o administrador do sistema deverá criar seu usuário e senha pelo **Painel Administrativo** (`/admin/`). Solicite ao administrador:
- Seu **nome de usuário**
- Sua **senha inicial**
- Seu **perfil de permissão** (Administrador, Gerente, Vendedor, Operador ou Almoxarife)

> **Dica:** Após o primeiro login, acesse `/admin/password_change/` para alterar sua senha.

### Sair do Sistema

Clique no seu nome (canto superior direito) → **Sair do Sistema**. Você será desconectado e redirecionado para a tela de login.

---

## 3. Painel Principal

O Dashboard é a tela inicial após o login. Ele apresenta um resumo visual da saúde do seu negócio:

### KPIs (Indicadores)

| Indicador | Descrição |
|---|---|
| **Total de Clientes** | Quantidade total de clientes cadastrados |
| **Total de Produtos** | Quantidade de produtos no catálogo |
| **Total de Vendas** | Número total de vendas realizadas |
| **Faturamento do Mês** | Soma das vendas confirmadas no mês atual |
| **Saldo em Caixa** | Soma dos saldos de todas as contas bancárias |
| **Estoque Baixo** | Produtos com estoque abaixo do mínimo configurado |
| **Clientes Novos** | Clientes cadastrados no mês corrente |

### Gráfico de Faturamento

Selecione o período desejado: **7 dias**, **30 dias**, **6 meses** ou **12 meses**.

### Seções Adicionais

- **Produtos Mais Vendidos** — ranking dos 5 produtos com maior volume de vendas
- **Vendas Recentes** — últimas 5 vendas registradas no sistema
- **Lembretes** — bloco de notas rápidas e tarefas pendentes
- **Reembolsos Pendentes** — notificação de reembolsos aguardando pagamento

---

## 4. Gestão de Clientes

**Menu:** Gestão Comercial → **Gestão de Clientes**

### Listar Clientes

A tela principal exibe todos os clientes cadastrados com opções de busca e filtragem.

### Cadastrar Novo Cliente

1. Clique em **Novo Cliente**.
2. Preencha os campos:
   - **Nome** (obrigatório)
   - **Tipo:** Pessoa Física (CPF) ou Pessoa Jurídica (CNPJ)
   - **CPF/CNPJ** (obrigatório, único no sistema)
   - **E-mail**, **Telefone**, **Endereço**, **Cidade**, **Estado**, **CEP** (opcionais)
   - **Ativo:** define se o cliente está ativo no sistema
3. Clique em **Salvar**.

### Editar Cliente

Na lista de clientes, clique no ícone de **lápis** (✏️) ao lado do cliente desejado, altere os campos e clique em **Salvar**.

### Visualizar Detalhes

Clique no **nome do cliente** para ver seus detalhes completos e o histórico de vendas associado.

### Excluir Cliente

Clique no ícone de **lixeira** (🗑️), confirme a exclusão na tela de confirmação.

> **Atenção:** A exclusão de um cliente remove permanentemente seus dados. Prefira **desativar** o cliente (desmarcar "Ativo") para manter o histórico.

---

## 5. Gestão de Vendas

**Menu:** Gestão Comercial → **Gestão de Vendas**

### Listar Vendas

Exibe todas as vendas com status, cliente, valor e data. Os status possíveis são:

| Status | Significado |
|---|---|
| 🟡 **Rascunho** | Venda em elaboração, ainda não confirmada |
| 🟢 **Confirmada** | Venda efetivada, conta como faturamento |
| 🔵 **Entregue** | Produtos entregues ao cliente |
| 🔴 **Cancelada** | Venda cancelada |

### Registrar Nova Venda

1. Clique em **Nova Venda**.
2. Selecione o **Cliente**.
3. Adicione **Itens da Venda**:
   - Escolha o produto (vinculado ao estoque) ou digite o nome manualmente
   - Informe a **quantidade** e o **preço unitário**
   - O **subtotal** de cada item é calculado automaticamente
4. O sistema calcula automaticamente o **Subtotal** e **Valor Total**.
5. Opcionalmente, aplique um **Desconto**.
6. Escolha o **Status** (Rascunho, Confirmada, etc.).
7. Clique em **Salvar**.

### O que acontece ao confirmar uma venda?

- O sistema cria automaticamente uma **transação financeira** do tipo "Receita" no módulo Financeiro.
- Ao cancelar uma venda confirmada, a transação é revertida automaticamente.

### Gerar Nota Fiscal a partir de uma Venda

Na tela de detalhes da venda, clique em **Gerar Nota Fiscal**. O sistema preenche automaticamente os dados da NF com base na venda.

### Excluir Venda

Vendas podem ser excluídas clicando no ícone 🗑️. Se a venda possuía transação financeira, ela é revertida automaticamente.

---

## 6. Gestão de Produtos e Estoque

**Menu:** Gestão de Estoque → **Gestão de Produtos**

### 6.1 Produtos

#### Listar Produtos
Tela com todos os produtos cadastrados, mostrando SKU, nome, categoria, preços e status.

#### Cadastrar Produto

1. Clique em **Novo Produto**.
2. Preencha:
   - **Nome** (obrigatório)
   - **SKU** — código único. Se deixado em branco, o sistema gera automaticamente (ex: `PRD-AB12-260512`)
   - **Categoria** — classifica o produto
   - **Preço de Custo** — quanto você paga pelo produto
   - **Preço de Venda** — quanto você cobra do cliente
   - **Descrição** (opcional)
   - **Ativo** — se o produto está disponível
3. Clique em **Salvar**.

> **Validações automáticas:**
> - O preço de custo não pode ser negativo
> - O preço de venda não pode ser negativo
> - O preço de venda deve ser ≥ preço de custo

#### Margem de Lucro

O sistema calcula automaticamente a **margem de lucro** percentual: `((Preço Venda - Preço Custo) / Preço Custo) × 100`

### 6.2 Categorias

Agrupe seus produtos em categorias (ex: Eletrônicos, Alimentos, Ferramentas). Acesse pela tela de Produtos → aba **Categorias**.

### 6.3 Controle de Estoque

Cada produto possui um registro de estoque associado com:

- **Quantidade atual** em estoque
- **Quantidade mínima** — quando o estoque atinge esse valor, aparece o alerta "Estoque Baixo" no Dashboard
- **Localização** — onde o produto fica armazenado

### 6.4 Movimentações de Estoque

Registre entradas e saídas do estoque:

| Tipo | Efeito |
|---|---|
| **Entrada** | Aumenta a quantidade em estoque |
| **Saída** | Diminui a quantidade (valida se há saldo suficiente) |
| **Ajuste** | Define a quantidade para um valor específico (inventário) |
| **Devolução** | Aumenta a quantidade (produto devolvido) |

Para registrar: Acesse o produto → **Nova Movimentação** → Informe tipo, quantidade e motivo → **Salvar**.

> **Segurança:** Saídas com quantidade maior que o saldo disponível são bloqueadas.

### 6.5 Relatório de Estoque

Disponível na tela de Produtos, mostra uma visão consolidada do valor total em estoque e itens em alerta.

---

## 7. Gestão Financeira

### 7.1 Gestão de Caixa (Transações)

**Menu:** Gestão Financeira → **Gestão de Caixa**

Gerencie todas as entradas e saídas de dinheiro do seu negócio.

#### Tipos de Transação

| Tipo | Descrição |
|---|---|
| **Receita** | Dinheiro que entra (vendas, serviços) |
| **Despesa** | Dinheiro que sai (aluguel, contas, compras) |

#### Campos de uma Transação

- **Tipo** (Receita ou Despesa)
- **Categoria** (ex: Vendas, Aluguel, Material)
- **Descrição** — detalhe da transação
- **Valor** (em R$)
- **Data da Transação** — quando aconteceu
- **Data de Vencimento** (opcional) — para contas a pagar/receber
- **Conta Bancária** — conta associada
- **Paga** — se o pagamento/recebimento já foi efetivado

> **Automático:** Vendas confirmadas geram transações de receita automaticamente.

### 7.2 Gestão de Receitas

**Menu:** Gestão Financeira → **Gestão de Receitas**

Visualize apenas as transações do tipo "Receita" de forma filtrada.

### 7.3 Gestão de Reembolsos

**Menu:** Gestão Financeira → **Gestão de Reembolsos**

Controle pedidos de reembolso de colaboradores.

#### Campos do Reembolso

- **Colaborador** — quem está pedindo o reembolso
- **Nome do Solicitante** (manual, caso não haja perfil)
- **Prioridade:** 🔴 Alta, 🟡 Média, 🟢 Baixa
- **Item/Descrição** — o que foi comprado
- **Valor** (R$)
- **Data da Compra**
- **Comprovante** — upload de imagem ou PDF do recibo
- **Reembolsado?** — marca quando o reembolso foi pago
- **Observações**

> **Notificação:** Reembolsos pendentes aparecem como alerta 🔔 no topo de todas as telas.

### 7.4 Contas Bancárias

Cadastre suas contas bancárias com: Banco, Agência, Conta, Saldo e Status (Ativa/Inativa). As transações podem ser vinculadas a contas específicas.

---

## 8. Gestão Fiscal

**Menu:** Gestão Fiscal → **Gestão de Notas**

### Listar Notas Fiscais

Exibe todas as NFs com número, série, cliente, valor e status.

### Status da Nota Fiscal

| Status | Descrição |
|---|---|
| 📝 **Rascunho** | NF criada, pode ser editada livremente |
| ✅ **Emitida** | NF emitida oficialmente |
| ❌ **Cancelada** | NF cancelada (somente se estava emitida) |

### Criar Nota Fiscal

1. Clique em **Nova Nota Fiscal**.
2. Preencha:
   - **Cliente** (obrigatório)
   - **Venda vinculada** (opcional — pode vincular a uma venda existente)
   - **Número** e **Série** da NF
   - **Data de Emissão** e **Data de Saída**
   - **Descrição dos itens**
   - **Valores:** Subtotal, Desconto, ICMS, IPI
   - O **Valor Total** é calculado automaticamente: `Subtotal - Desconto + ICMS + IPI`
3. Clique em **Salvar**.

### Emitir Nota Fiscal

Na tela de detalhes, clique em **Emitir NF**. Somente rascunhos podem ser emitidos.

### Cancelar Nota Fiscal

Na tela de detalhes, clique em **Cancelar NF**. Somente NFs emitidas podem ser canceladas.

### Validações

- Número e série são obrigatórios
- Valores não podem ser negativos
- Desconto não pode ser maior que o subtotal
- Data de saída não pode ser anterior à emissão

---

## 9. Gestão de Almoxarifado

**Menu:** Gestão de Estoque → **Gestão de Almoxarifado**

O Almoxarifado controla os **materiais de uso interno** da empresa (não o que você vende, mas o que você consome trabalhando).

### 9.1 Dashboard do Almoxarifado

Visão geral com KPIs: total de itens, locais, setores e valor em estoque.

### 9.2 Estrutura de Armazenamento

#### Locais de Armazenamento
Depósitos, galpões ou almoxarifados onde os materiais ficam guardados.

#### Endereços
Posições específicas dentro de cada local: **Corredor**, **Estante** e **Prateleira**. Cada endereço possui um **código único** que pode ser usado para gerar QR Codes/etiquetas.

Exemplo de endereço: `Almoxarifado Central > C:A E:02 P:03`

### 9.3 Setores

Represente os setores/departamentos da empresa (ex: Produção, Administração, Manutenção). Cada setor pode ter um **responsável** vinculado.

### 9.4 Saldos

Controle a quantidade de cada produto em cada local/endereço, com quantidade mínima para alerta.

### 9.5 Requisições Internas

Quando um setor precisa de material:

1. O solicitante acessa **Nova Requisição**.
2. Seleciona o **Setor**, o **Local de Origem** (almoxarifado).
3. Adiciona os **Itens** desejados com a quantidade.
4. Escreve uma **Justificativa**.
5. Clique em **Salvar** (status: Solicitado).

#### Fluxo de Aprovação

| Status | Significado |
|---|---|
| **Solicitado** | Aguardando análise do gestor |
| **Aprovado** | Aprovado, material pode ser retirado |
| **Recusado** | Solicitação negada pelo gestor |
| **Entregue** | Material entregue ao setor |
| **Cancelado** | Requisição cancelada |

### 9.6 Central de Etiquetas

Gere etiquetas com QR Code para identificar prateleiras e locais de armazenamento.

---

## 10. Gestão de Produção

**Menu:** Gestão Operacional → **Gestão de Produção (PCP)**

### 10.1 Fichas Técnicas (Engenharia)

A Ficha Técnica é a "receita" de fabricação de um produto. Ela define:

- **Produto Final** — o que será fabricado
- **Descrição** — instruções de montagem
- **Tempo Estimado** — em minutos
- **Itens/Insumos** — cada material necessário com a quantidade por unidade

O sistema calcula o **custo total de materiais** automaticamente.

### 10.2 Ordens de Produção (OP)

Para fabricar produtos:

1. Clique em **Nova Ordem de Produção**.
2. Selecione a **Ficha Técnica** (produto a fabricar).
3. Informe a **Quantidade Planejada**.
4. Opcionalmente, informe o **Custo de Mão de Obra**.
5. Clique em **Salvar**.

#### Status da OP

| Status | Descrição |
|---|---|
| **Aberta/Planejada** | OP criada, aguardando início |
| **Em Produção** | Fabricação em andamento |
| **Finalizada** | Produção concluída, estoque atualizado |
| **Cancelada** | OP cancelada |

#### Finalizar Produção

Ao finalizar uma OP, o sistema automaticamente:

1. ✅ **Consome os insumos** do Almoxarifado (FIFO)
2. ✅ **Gera entrada no estoque** de vendas com o produto acabado
3. ✅ **Calcula o custo total** de materiais

> **Verificação:** Antes de finalizar, o sistema verifica se há saldo suficiente de todos os insumos. Caso falte algum material, a finalização é bloqueada.

---

## 11. Ordens de Serviço

**Menu:** Gestão Operacional → **Ordens de Serviço (O.S.)**

### Tipos de O.S.

| Tipo | Uso |
|---|---|
| **Serviço ao Cliente** | Serviço prestado para um cliente externo |
| **Manufatura Interna** | Trabalho interno de fabricação |
| **Manutenção Interna** | Manutenção de equipamentos ou instalações |

### Campos da O.S.

- **Cliente** (para serviços externos)
- **Solicitante** e **Responsável**
- **Tipo** e **Status** (Aberta → Em Execução → Finalizada / Cancelada)
- **Data de Início** e **Data de Fim**
- **Descrição do Problema/Pedido**
- **Laudo Técnico** — ações realizadas
- **Valor do Serviço** e **Valor de Materiais**
- **Itens consumidos** — materiais retirados do almoxarifado durante a execução

O **Valor Total** é calculado automaticamente: `Valor Serviço + Valor Materiais`.

---

## 12. Gestão de Compras

**Menu:** Gestão Operacional → **Gestão de Compras**

### 12.1 Fornecedores

Cadastre seus fornecedores com: Nome, CNPJ, E-mail, Telefone, Endereço e Status.

### 12.2 Pedidos de Compra

1. Crie um **Novo Pedido de Compra**.
2. Adicione os **Itens** (produtos do estoque) com quantidades.
3. Defina a **Data Prevista** de entrega.

#### Fluxo do Pedido

| Status | Descrição |
|---|---|
| **Solicitado** | Pedido criado, aguardando cotação |
| **Em Cotação (Mapa)** | Cotações sendo recebidas |
| **Aprovado** | Pedido aprovado para compra |
| **Recebido** | Material recebido e no estoque |
| **Cancelado** | Pedido cancelado |

### 12.3 Cotações (Mapa de Cotação)

Para cada pedido de compra, você pode registrar cotações de diferentes fornecedores:

- **Fornecedor**
- **Valor Total**
- **Prazo de Entrega** (em dias)
- **Condições de Pagamento**
- **Arquivo Anexo** (PDF do orçamento)
- **Vencedor** — marque a cotação escolhida

---

## 13. BI e Relatórios

**Menu:** Menu Principal → **BI de Resultados**

### Dashboard de BI

Painel gerencial com gráficos e indicadores avançados para análise do negócio.

### Relatórios Disponíveis

| Relatório | Descrição |
|---|---|
| **DRE (PDF)** | Demonstrativo de Resultado do Exercício |
| **Relatório de Consumo** | Consumo de materiais do almoxarifado |
| **Relatório de Estoque** | Posição atual do estoque com valores |
| **Relatório Fiscal** | Consolidado de notas fiscais emitidas |
| **Relatório Financeiro** | Resumo de receitas e despesas por período |

> **Dica:** Todos os relatórios podem ser **impressos** usando a função de impressão do navegador (Ctrl+P). O sistema oculta automaticamente menus e botões na versão impressa.

---

## 14. Lembretes e Anotações

Disponível diretamente no **Dashboard** e no menu dedicado.

### Criar Lembrete

1. Clique em **Novo Lembrete**.
2. Preencha:
   - **Título** — resumo da tarefa
   - **Conteúdo/Nota** — detalhes
   - **Data do Serviço** (opcional)
   - **Categoria:**
     - 🔴 **Prioritário** — urgente
     - 🔵 **Manutenção** — rotina
     - 🟢 **Orçamento** — pendente
3. Clique em **Salvar**.

### Gerenciar Lembretes

- **Concluir:** Clique no botão de check (✓) para marcar como concluído
- **Excluir:** Clique no ícone de lixeira (🗑️)
- **Histórico:** Acesse a lista completa para ver todos os lembretes (pendentes e concluídos)

---

## 15. Personalização (White Label)

**Acesso:** Menu do Usuário (canto superior direito) → **Personalizar Marca**

Personalize o sistema com a identidade visual da sua empresa:

- **Nome da Empresa** e **CNPJ**
- **Logo da Empresa** — aparece na barra lateral
- **Dados de contato:** E-mail, Telefone, Endereço
- **Cidade**, **Estado**, **CEP**

Após salvar, o nome e logo da empresa aparecem automaticamente em todas as telas.

---

## 16. Configurações e Administração

**Menu:** Gestão de Configurações → **Gestão de Sistema**

Acessa o **Painel Administrativo do Django**, onde é possível:

- Gerenciar **usuários** (criar, editar, desativar)
- Gerenciar **perfis** e permissões
- Cadastrar **empresas**
- Administrar **contas bancárias**
- Configurações avançadas de todos os módulos

### Modo Escuro / Claro

Clique no botão 🌙 **Escuro** / ☀️ **Claro** no topo da tela. A preferência é salva automaticamente no seu navegador.

---

## 17. Perguntas Frequentes

### Como recuperar minha senha?
Entre em contato com o administrador do sistema para que ele redefina sua senha pelo painel administrativo.

### Posso usar o sistema no celular?
Sim! O sistema é **responsivo** e se adapta a telas de celulares e tablets.

### O que significa "Estoque Baixo" no Dashboard?
Significa que a quantidade em estoque de algum produto atingiu ou ficou abaixo da **quantidade mínima** configurada.

### Como faço backup dos dados?
O administrador do sistema deve realizar backups periódicos do banco de dados. Consulte o Guia Técnico de Implantação para os comandos.

### Posso desfazer uma venda?
Sim. Você pode **cancelar** uma venda alterando o status para "Cancelada" ou **excluí-la**. Em ambos os casos, as transações financeiras vinculadas são revertidas automaticamente.

### Como gero uma nota fiscal?
Você pode criar uma NF manualmente pelo menu Fiscal, ou gerá-la automaticamente a partir de uma venda confirmada na tela de detalhes da venda.

### O que é uma Ficha Técnica?
É a "receita" de fabricação de um produto. Define quais materiais (insumos) e quantidades são necessários para produzir uma unidade do produto final.

### Posso personalizar o sistema com a minha marca?
Sim! Use a opção "Personalizar Marca" no menu do usuário para inserir o nome, logo e dados da sua empresa.

---

**SISTEMA GESTOR** — Tecnologia para o crescimento do PME brasileiro.  
© 2026 JR Solutions Tecnologia. Todos os direitos reservados.
