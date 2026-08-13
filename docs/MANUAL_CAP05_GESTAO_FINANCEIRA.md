# 📘 MANUAL DO USUÁRIO — SISTEMA GESTOR

### Capítulo 5: Gestão Financeira e Caixa

**Versão:** 1.0 — Maio/2026  
**Módulo:** Gestão Financeira

---

## 📋 Índice deste Capítulo

1. [Visão Geral do Financeiro](#1-visão-geral-do-financeiro)
2. [Gestão de Contas Bancárias](#2-gestão-de-contas-bancárias)
3. [Gestão de Caixa (Receitas e Despesas)](#3-gestão-de-caixa-receitas-e-despesas)
4. [Gestão de Reembolsos (Colaboradores)](#4-gestão-de-reembolsos-colaboradores)
5. [O Sino de Alerta de Reembolsos 🔔](#5-o-sino-de-alerta-de-reembolsos)
6. [Perguntas Frequentes](#6-perguntas-frequentes)

---

## 1. Visão Geral do Financeiro

O módulo financeiro é o cofre da empresa. É aqui que você controla todo o dinheiro que **entra** (Receitas), todo o dinheiro que **sai** (Despesas), e gerencia os pedidos de **Reembolso** da sua equipe.

**Onde acessar?**  
No Menu Lateral, você verá a seção **Gestão Financeira** com três opções:
- 💳 **Gestão de Caixa** (Visão completa de tudo)
- 💹 **Gestão de Receitas** (Mostra apenas as entradas de dinheiro)
- 📋 **Gestão de Reembolsos** (Controle de despesas da equipe)

---

## 2. Gestão de Contas Bancárias

Antes de lançar valores, é ideal ter as contas da empresa cadastradas. O sistema já vem com uma conta padrão chamada "Caixa Interno", mas você pode cadastrar suas contas do banco.

> **Acesso:** Menu de Configurações Administrativas (Restrito a Administradores).

Ao cadastrar uma conta bancária (Banco do Brasil, Nubank, Itaú), o sistema somará os saldos de todas elas e mostrará o **"Saldo em Caixa"** total lá no Dashboard principal!

---

## 3. Gestão de Caixa (Receitas e Despesas)

Na tela de **Gestão de Caixa**, você verá uma lista (extrato) com toda a movimentação da empresa.

### Tipos de Transação
O sistema usa cores para facilitar a identificação:
- 🟢 **Receita:** Dinheiro que entrou (vendas, serviços prestados, rendimentos).
- 🔴 **Despesa:** Dinheiro que saiu (pagamento de fornecedores, contas de luz, aluguel, salários).

### Como lançar uma movimentação manual:

Lembre-se que as Vendas (quando marcadas como Confirmadas) já geram Receitas automaticamente. Mas se você pagou a conta de luz, precisa lançar a Despesa na mão:

1. Clique em **"Nova Transação"**.
2. Escolha o **Tipo:** `Despesa`.
3. Preencha os campos essenciais:
   - **Descrição:** Ex: "Conta de Energia - Maio".
   - **Valor:** Ex: 150,00.
   - **Data da Transação:** Quando o pagamento foi feito.
   - **Categoria:** Ex: "Despesas Operacionais".
   - **Conta Bancária:** De qual conta o dinheiro saiu.
4. Marque a caixinha **"Paga"** (se já foi paga) e clique em **"Salvar"**.

> [!TIP]
> Se a conta for para o mês que vem, você pode lançar agora, preencher a **"Data de Vencimento"** e deixar a caixinha "Paga" **desmarcada**. Assim você cria um controle de "Contas a Pagar"!

---

## 4. Gestão de Reembolsos (Colaboradores)

Quando um funcionário compra algo para a empresa com o próprio dinheiro (ex: gasolina, pedágio, almoço com cliente), ele precisa ser reembolsado. O sistema tem uma tela exclusiva só para isso!

### Como pedir um reembolso:

1. Acesse **Gestão de Reembolsos**.
2. Clique em **"Novo Reembolso"**.
3. Preencha:
   - **Colaborador / Solicitante:** Quem está pedindo o dinheiro.
   - **Item/Descrição:** O que foi comprado (ex: "Abastecimento Carro Empresa").
   - **Valor:** R$ gasto.
   - **Data da Compra:** Quando a despesa ocorreu.
   - **Prioridade:** 🔴 Alta (urgente), 🟡 Média ou 🟢 Baixa.
   - **Comprovante:** Anexe a foto da notinha fiscal ou o PDF do recibo (Obrigatório em muitas empresas!).
4. Clique em **"Salvar"**.

O status ficará como **"Pendente"** até o gestor financeiro pagar.

---

## 5. O Sino de Alerta de Reembolsos 🔔

Para o financeiro não esquecer de pagar a equipe, o sistema conta com uma notificação inteligente.

Se existir qualquer reembolso pendente no sistema, um **sino vermelho 🔔** começará a piscar lá na barra superior (no topo da tela, perto do seu nome).

1. Clique no sino.
2. Uma janelinha se abrirá mostrando **quantos** reembolsos estão aguardando pagamento.
3. Clique no botão azul "Gerar Reembolsos" para ir direto para a tela de aprovação.

### Como dar o reembolso como pago:
O gestor financeiro abre o pedido, confere o valor e a foto do comprovante e, após fazer o PIX/Transferência para o colaborador, edita o pedido e marca a caixinha **"Reembolsado?"**. 
O pedido sai da fila de pendentes e o sino para de piscar.

---

## 6. Perguntas Frequentes

### ❓ "A venda que fiz gerou uma receita, mas o valor ficou 'Pendente' (Não Paga). Por quê?"
Isso acontece se o cliente fez a venda, mas disse que ia pagar depois (fiado ou boleto). Quando o dinheiro efetivamente cair na conta, você deve vir na Gestão de Caixa, editar a Receita e marcar como **"Paga"**.

### ❓ "Posso excluir um reembolso depois que ele foi pago?"
Sim, mas não é recomendado. O ideal é manter o histórico. Se houve um erro, edite o valor ou adicione uma observação no campo apropriado.

### ❓ "Como anexo a foto do comprovante no celular?"
Na hora de criar o reembolso, clique no botão "Escolher Arquivo". O celular abrirá a opção para "Tirar uma foto" na hora com a câmera ou escolher uma foto da galeria de imagens.

### ❓ "O Saldo em Caixa do sistema não está batendo com o do meu banco."
Isso ocorre quando existem transações que aconteceram no banco, mas esqueceram de ser lançadas no sistema (ex: taxas bancárias de R$ 15,00). Você precisa lançar essas pequenas despesas no sistema para os valores baterem.

---

> **SISTEMA GESTOR** — Tecnologia para o crescimento do PME brasileiro.  
> © 2026 JR Solutions Tecnologia. Todos os direitos reservados.
