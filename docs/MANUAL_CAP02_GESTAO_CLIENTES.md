# 📘 MANUAL DO USUÁRIO — SISTEMA GESTOR

### Capítulo 2: Gestão de Clientes

**Versão:** 1.0 — Maio/2026  
**Módulo:** Gestão Comercial > Gestão de Clientes

---

## 📋 Índice deste Capítulo

1. [Visão Geral do Módulo](#1-visão-geral-do-módulo)
2. [A Tela de Clientes (Listagem)](#2-a-tela-de-clientes-listagem)
3. [Como Cadastrar um Novo Cliente](#3-como-cadastrar-um-novo-cliente)
4. [Dicas de Preenchimento: PF vs PJ](#4-dicas-de-preenchimento-pf-vs-pj)
5. [Como Editar um Cliente](#5-como-editar-um-cliente)
6. [Detalhes e Histórico do Cliente](#6-detalhes-e-histórico-do-cliente)
7. [Inativar vs Excluir](#7-inativar-vs-excluir)
8. [Perguntas Frequentes](#8-perguntas-frequentes)

---

## 1. Visão Geral do Módulo

A **Gestão de Clientes** é o coração do setor comercial. Neste módulo, você centraliza todas as informações das pessoas e empresas que compram de você.

Manter este cadastro atualizado é fundamental porque os dados daqui são usados em todo o sistema:
- Para gerar vendas e orçamentos
- Para emitir Ordens de Serviço
- Para preencher automaticamente as Notas Fiscais

> **Acesso:** No Menu Lateral, vá em **Gestão Comercial** → **Gestão de Clientes**.

---

## 2. A Tela de Clientes (Listagem)

Ao abrir o módulo, você verá a lista com todos os seus clientes cadastrados:

![Tela de Lista de Clientes](C:\Users\roque\.gemini\antigravity\brain\92288090-475a-4b8c-b959-dd91c417ff35\tela_lista_clientes_1778713698179.png)

### Ferramentas disponíveis na tela:

| Ferramenta | O que faz |
|------------|-----------|
| 🔍 **Busca (Pesquisa)** | Digite parte do nome, CPF/CNPJ ou telefone para encontrar um cliente rapidamente. |
| 🟢 **Status** | Uma etiqueta verde indica que o cliente está **Ativo**. Uma cinza indica que está **Inativo**. |
| ➕ **Botão "Novo Cliente"** | Inicia o cadastro de um novo cliente. |
| ⚙️ **Coluna "Ações"** | Botões rápidos para **Editar** (✏️ lápis) ou **Excluir** (🗑️ lixeira). |

> [!TIP]
> Use a barra de busca para verificar se um cliente já está cadastrado antes de criar um novo, evitando cadastros duplicados!

---

## 3. Como Cadastrar um Novo Cliente

Para adicionar um cliente ao sistema:

1. Na tela de Clientes, clique no botão azul **"Novo Cliente"**.
2. O formulário de cadastro se abrirá:

![Tela de Cadastro de Cliente](C:\Users\roque\.gemini\antigravity\brain\92288090-475a-4b8c-b959-dd91c417ff35\tela_cadastro_cliente_1778713795746.png)

### Passo a passo do preenchimento:

**Dados Principais (Obrigatórios):**
- **Nome:** Digite o nome completo ou a Razão Social.
- **Tipo:** Escolha entre **Pessoa Física** ou **Pessoa Jurídica**.
- **CPF / CNPJ:** Digite apenas os números (o sistema colocará os pontos e traços automaticamente). Este número não pode se repetir em outro cadastro!
- **Status Ativo:** Deixe marcado para que o cliente apareça na hora de fazer uma venda.

**Contato & Endereço (Opcionais, mas recomendados):**
- **E-mail:** Importante para enviar orçamentos e NFs.
- **Telefone:** Principal meio de contato (WhatsApp).
- **Endereço Completo:** Rua, número, bairro, cidade, estado e CEP (obrigatório se for emitir Nota Fiscal no futuro).

3. Após preencher, clique no botão **"Salvar"**.
4. Uma mensagem verde de sucesso aparecerá e o cliente já estará na sua lista.

---

## 4. Dicas de Preenchimento: PF vs PJ

O sistema adapta algumas regras dependendo se o seu cliente é uma Pessoa Física (PF) ou Pessoa Jurídica (PJ).

| Tipo | Documento Exigido | Dica para Notas Fiscais |
|------|-------------------|-------------------------|
| **Pessoa Física (PF)** | CPF (11 dígitos) | Ideal para consumidor final (varejo). |
| **Pessoa Jurídica (PJ)** | CNPJ (14 dígitos) | Além do CNPJ, ao emitir nota para PJ, preencha corretamente o endereço completo e verifique se a empresa possui Inscrição Estadual (IE). |

> [!IMPORTANT]
> O sistema não permite cadastrar **dois clientes com o mesmo CPF ou CNPJ**. Se você tentar, o sistema mostrará um erro avisando que o documento já existe.

---

## 5. Como Editar um Cliente

Se você digitou algo errado ou se o cliente mudou de telefone/endereço:

1. Encontre o cliente na lista.
2. Na coluna **Ações**, clique no ícone de **Lápis (✏️)**.
3. Altere as informações necessárias no formulário.
4. Clique em **"Salvar"**.

---

## 6. Detalhes e Histórico do Cliente

Você quer saber o que este cliente já comprou? 

1. Na lista de clientes, clique em cima do **Nome do Cliente** (ele funciona como um link).
2. Uma nova tela se abrirá mostrando:
   - Os dados completos do cliente em formato de cartão.
   - **Histórico de Vendas:** Uma tabela com todas as vendas já feitas para ele, com status (Confirmada, Entregue, etc.) e valores totais.

Esta visão é excelente para entender o perfil de compra do seu cliente!

---

## 7. Inativar vs Excluir

Com o tempo, sua base de clientes pode crescer muito. Como lidar com clientes antigos?

### Excluir (🗑️ Lixeira)
- **O que faz:** Apaga permanentemente o cadastro.
- **Quando usar:** Quando você cadastrou algo errado por engano.
- **Limitação:** Você **NÃO** pode excluir um cliente que já possui uma Venda ou Ordem de Serviço registrada no nome dele. O sistema protegerá esses dados para não quebrar seu histórico financeiro.

### Inativar (Desmarcar "Ativo")
- **O que faz:** Mantém o histórico do cliente salvo, mas ele deixa de aparecer na lista na hora de fazer novas vendas.
- **Como fazer:** Clique em Editar (✏️) e desmarque a caixinha **"Ativo"**, depois salve.
- **Quando usar:** Esta é a **melhor prática** para clientes antigos, problemáticos ou que fecharam as portas.

---

## 8. Perguntas Frequentes

### ❓ "Estou tentando salvar, mas aparece 'CPF/CNPJ já cadastrado'. E agora?"
Isso significa que este documento já existe na sua base. Use a barra de busca na lista de clientes, digite o CPF/CNPJ e você encontrará o cadastro original para editá-lo.

### ❓ "Não consigo excluir um cliente, o botão de lixeira dá erro."
Se o cliente tiver feito qualquer compra (Venda) com você no passado, a exclusão é bloqueada por segurança. A solução correta é **Inativar** o cliente (veja a seção 7).

### ❓ "O CEP busca o endereço automaticamente?"
Na versão atual, o preenchimento de endereço é manual, mas recomendamos preencher no formato completo (Rua X, 123 - Bairro Y) para evitar problemas na emissão de Notas Fiscais depois.

### ❓ "Posso cadastrar um cliente sem CPF?"
Para usar todas as funcionalidades do sistema (especialmente vendas oficiais e notas fiscais), o CPF/CNPJ é o identificador único exigido.

---

> **SISTEMA GESTOR** — Tecnologia para o crescimento do PME brasileiro.  
> © 2026 JR Solutions Tecnologia. Todos os direitos reservados.
