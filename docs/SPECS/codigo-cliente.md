# Spec — Código do cliente por empresa

| Campo | Valor |
|---|---|
| **Versão** | 1.0 |
| **Status** | aprovado — na fila, ainda não implementar |
| **Autor** | José Roque / Hermes |
| **Data** | 2026-10-10 |
| **Módulos afetados** | clientes, vendas (só o texto na tela da venda) |
| **Plano** | todos |

DECISÃO (José, fechou em 2026-10-10): o número que aparece no cadastro do cliente passa a ser um código da empresa, começando em 01. O id interno do banco não zera e deixa de aparecer. Fechar a spec e colocar na fila. Não codar até ele mandar executar a fila.

---

## 1. Objetivo (por que?)

Quem cadastra o primeiro cliente espera ver 01. Hoje a lista mostra um número alto, que não é daquela empresa. O gestor precisa de um código curto e estável, por empresa.

## 2. Contexto / Cenário atual

Inspecionado em 2026-10-10:

- `Cliente` não tem código próprio. A lista (`templates/meigestao_app/clientes/cliente_list.html`) mostra `#{{ cliente.id }}` na coluna ID.
- A venda mostra `ID Cadastro: {{ venda.cliente.id }}`.
- Esse `id` é o contador único da tabela, de todas as empresas. Teste, demonstração, cliente apagado e cliente de outra empresa fazem o número subir. Apagar não devolve o número.
- Os links internos (editar, ver, nova venda) usam esse `id` na URL. Isso não é o número que o usuário lê. Não trocar a URL.
- Cliente pertence a uma empresa (`empresa`). O plano básico acessa clientes.

## 3. Escopo

- **Incluído:**
  - Código numérico por empresa. O primeiro cliente da empresa é 01. O próximo é 02, e assim por diante.
  - Clientes que já existem recebem o código na ordem em que foram cadastrados naquela empresa.
  - A lista de clientes e o texto "ID Cadastro" na venda passam a mostrar esse código, com no mínimo 2 dígitos (01, 02, …, 100).
  - A coluna deixa de se chamar ID. Passa a se chamar Código.
- **Excluído (não-escopo):**
  - Zerar ou reaproveitar o `id` interno do banco.
  - Reusar código de cliente apagado. O próximo continua a sequência, para o 01 de ontem não virar outra pessoa.
  - Mudar a URL de editar, ver ou vender.
  - Fazer o mesmo código em produto, venda ou ordem de serviço nesta leva.
  - Pacote de textos, nota discreta, nosso boleto e etiqueta limpa.

## 4. Requisitos Funcionais (o que o sistema FAZ)

- RF1 — Ao cadastrar o primeiro cliente de uma empresa, o código gravado é 1 e a tela mostra 01.
- RF2 — O cliente seguinte da mesma empresa recebe o próximo número, mesmo que alguém tenha apagado um código no meio.
- RF3 — Outra empresa, no mesmo sistema, também começa em 01. O código de uma não interfere na outra.
- RF4 — A lista não mostra mais o `id` interno.
- RF5 — Na venda, o texto deixa de ser "ID Cadastro" com o `id` interno e passa a mostrar o código da empresa.
- RF6 — Clientes já cadastrados ganham código na ordem de `criado_em`, sem mudar o `id` interno.

## 5. Requisitos Não-Funcionais

- Dois cadastros ao mesmo tempo na mesma empresa não podem ficar com o mesmo código.
- O código não muda depois de gravado.
- Isolamento por empresa, como o resto do cadastro.

## 6. Dados / Modelo

Campo novo em `Cliente`:

- `codigo` — inteiro, obrigatório, único junto com `empresa`.
- Nome na tela: Código.
- Não é o `id`.

Na gravação, o código é o maior código daquela empresa mais 1. Se não houver nenhum, é 1.

A migração preenche os clientes atuais, por empresa, em ordem de `criado_em` e `id`.

## 7. Fluxo / Telas

1. Usuário cadastra o cliente como hoje.
2. Ao salvar, o sistema atribui o código. O usuário não digita.
3. A lista mostra `#01`.
4. A venda mostra o mesmo código.

Nenhuma rota nova.

## 8. Segurança / Restrições por Plano e Empresa

- O código é calculado só com clientes da empresa do usuário.
- Plano: todos os que já cadastram cliente, inclusive básico.
- A URL continua com o `id` interno. Não passar a buscar cliente só pelo código na URL, para não abrir cadastro de outra empresa com o mesmo 01.

## 9. Critérios de Aceite (TESTES — o "check")

- CA1 — Primeiro cliente da empresa A grava `codigo=1`. A lista contém `#01` e não contém o `id` interno na coluna de código.
- CA2 — Segundo cliente da empresa A grava `codigo=2`.
- CA3 — Primeiro cliente da empresa B também grava `codigo=1`.
- CA4 — Apagar o cliente 01 da empresa A não faz o próximo nascer como 01. Nasce com o número seguinte.
- CA5 — A tela da venda mostra o código e não mostra o rótulo "ID Cadastro" com o `id` interno.
- CA6 — Dois cadastros simultâneos na mesma empresa não gravam o mesmo código.
- CA7 — A suíte de clientes que já existe continua verde.

## 10. Riscos / Dependências

- Risco: alguém já anotou o `id` interno num papel. Mitigação: o código novo é o número da empresa; o `id` interno continua existindo, só sai da tela.
- Não mexe em sequência do SQLite nem do Postgres.
- Implementar só quando José mandar executar a fila. Branch `feature/codigo-cliente`, um teste por critério, depois o código mínimo.

---

## Fluxo de trabalho

1. Spec escrita e aprovada em 2026-10-10.
2. Na fila: `docs/SPECS/FILA-ATUALIZACOES.md`, item 3.
3. Implementar só sob ordem, com TDD contra os CA.
4. Verificar, deploy com backup, validar ao vivo, então marcar esta spec como `implementado`.
