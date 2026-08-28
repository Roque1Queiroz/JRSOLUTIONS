# Spec — Modelo de tabela para importação de CSV (Clientes e Produtos)

> Modelo de **Spec-Driven Development** (Engineering com Agentes Inteligentes — cap. 6).
> Preencha ANTES de gerar código. A IA (Hermes) implementa contra esta spec; o check
> (`pytest`/`hermes verify`) só "entrega" o que passa nos critérios de aceite.

| Campo | Valor |
|---|---|
| **Versão** | 1.0 |
| **Status** | implementado |
| **Autor** | José Roque |
| **Data** | 2026-08-27 |
| **Módulos afetados** | clientes, estoque, core (utils) |
| **Plano** | todos |

---

## 1. Objetivo (por que?)
Reduzir erros de quem importa dados via CSV no Sistema Gestor: usuários leigos não sabem
quais colunas o sistema espera. A funcionalidade entrega um **arquivo CSV de modelo**
(cabeçalho pronto + linha de exemplo) com um clique, dentro da própria tela de importação,
para a pessoa preencher e reenviar corretamente.

## 2. Contexto / Cenário atual
- O sistema já importa CSV em **Clientes** (`clientes:cliente_import`) e **Produtos**
  (`estoque:produto_import`) usando `CSVImportService` (`core/utils/csv_importer.py`).
  - Clientes: obrigatórios `nome`, `cpf_cnpj`; opcionais `email`, `telefone`, `endereco`,
    `cidade`, `estado`, `cep` (delimitador `;` ou `,`; duplicidade por CPF/CNPJ por empresa).
  - Produtos: obrigatórios `nome`, `sku`, `preco_venda`; opcionais `categoria` (criada
    automaticamente), `preco_custo`, `estoque_inicial` (gera movimentação de entrada),
    `descricao`.
- **Dor**: não existe nenhum arquivo modelo. O usuário precisa adivinhar os nomes das
  colunas; qualquer erro de cabeçalho invalida a importação inteira ("Campos obrigatórios ausentes").

## 3. Escopo
- **Incluído:**
  - Botão "Baixar modelo CSV" dentro dos modais de importação de Clientes e de Produtos.
  - Dois endpoints GET autenticados que geram o CSV de modelo:
    `clientes:modelo_csv` (`/clientes/importar/modelo/`) e `estoque:modelo_csv`
    (`/estoque/produtos/importar/modelo/`).
  - Modelo com cabeçalho exato das colunas + **1 linha de exemplo** claramente marcada
    (prefixo `EXEMPLO -`) para o usuário substituir/apagar.
  - Encoding UTF-8 com BOM, delimitador `;` (padrão Excel BR) e quebra de linha CRLF —
    abre direto no Excel.
  - Dicas de importação atualizadas no modal de Clientes (lista completa de colunas opcionais).
- **Excluído (não-escopo):** alterar a lógica do importador existente; nova entidade de
  importação (categorias, OS etc.); upload de XLSX; pré-visualização de dados; validação
  de CPF/CNPJ no importador (fora do escopo; comportamento atual preservado).

## 4. Requisitos Funcionais (o que o sistema FAZ)
- RF1 — Como usuário logado, ao abrir o modal "Importar Clientes via CSV", posso clicar em
  **Baixar modelo CSV** e receber o arquivo `modelo_clientes.csv` com as colunas
  `nome;cpf_cnpj;email;telefone;endereco;cidade;estado;cep` e uma linha de exemplo.
- RF2 — Como usuário logado, ao abrir o modal "Importar Produtos via CSV", posso clicar em
  **Baixar modelo CSV** e receber o arquivo `modelo_produtos.csv` com as colunas
  `nome;sku;preco_venda;categoria;preco_custo;estoque_inicial;descricao` e uma linha de exemplo.
- RF3 — Um CSV baixado do modelo, preenchido com dados reais, é aceito pela importação
  existente (Clientes e Produtos) sem erro de cabeçalho.
- RF4 — O link do modelo está visível dentro do modal, junto ao seletor do arquivo.

## 5. Requisitos Não-Funcionais (qualidade/segurança)
- O download exige **usuário autenticado** (idêntico às telas do sistema).
- O modelo é **estático e genérico** (nenhum dado de empresa) → sem risco de vazamento
  multi-tenant.
- Compatível com Excel BR (BOM + `;` + CRLF) e com o importador (aceita `;` e `,`).
- Disponível para **todos os planos** (não é recurso premium).

## 6. Dados / Modelo
- **Sem mudança de schema.** Nenhum campo/tabela nova.
- Novo módulo `core/utils/csv_modelos.py` com as funções `modelo_clientes_csv(request)` e
  `modelo_produtos_csv(request)` (HttpResponse com `Content-Disposition: attachment`), com
  a mesma assinatura de `CSVImportService` para consistência.

## 7. Fluxo / Telas
1. Usuário logado abre **Clientes → Importar CSV** (ou **Estoque → Produtos → Importar CSV**).
2. No modal, clica em **Baixar modelo CSV** → baixa `modelo_clientes.csv` / `modelo_produtos.csv`.
3. Abre no Excel, substitui a linha de exemplo pelos dados reais (ou apaga), salva como CSV
   (ou mantém o .csv) e envia no mesmo modal → importação normal, sem erro de cabeçalho.

Rotas previstas:
- `clientes:modelo_csv` → `GET /clientes/importar/modelo/`
- `estoque:modelo_csv` → `GET /estoque/produtos/importar/modelo/`

## 8. Segurança / Restrições por Plano e Empresa
- `@login_required` nas duas views; usuário inativo/anônimo → redirect ao login.
- Modelo sem dados de empresa → isolamento multi-tenant intacto.
- Sem restrição por plano (todos os planos têm importação de CSV hoje).

## 9. Critérios de Aceite (TESTES — o "check")
- CA1 — `GET clientes:modelo_csv` sem login → redirect (302) para login.
- CA2 — `GET clientes:modelo_csv` logado → HTTP 200, `Content-Disposition` com
  `modelo_clientes.csv`, cabeçalho exato `nome;cpf_cnpj;email;telefone;endereco;cidade;estado;cep`
  e exatamente 1 linha de exemplo.
- CA3 — `GET estoque:modelo_csv` logado → HTTP 200, `Content-Disposition` com
  `modelo_produtos.csv`, cabeçalho exato `nome;sku;preco_venda;categoria;preco_custo;estoque_inicial;descricao`
  e exatamente 1 linha de exemplo.
- CA4 — POST `clientes:cliente_import` com CSV **nas mesmas colunas do modelo** (dados
  fictícios, delimitador `;`) → 302 e cliente criado no banco da empresa do usuário.
- CA5 — POST `estoque:produto_import` com CSV nas mesmas colunas do modelo → 302, produto
  criado, categoria criada/associada, estoque inicial aplicado (movimentação de entrada).
- CA6 — O CSV do modelo decodifica sem BOM visível e é lido pelo importador sem erro de
  cabeçalho (round-trip do modelo contra `CSVImportService`).
> A função só estará completa quando os critérios passarem (pytest + hermes verify).

## 10. Riscos / Dependências
- Linha de exemplo pode ser importada por engano se o usuário não a substituir → mitigado
  com prefixo `EXEMPLO -` bem visível e aviso nas dicas do modal ("substitua ou apague a
  linha de exemplo").
- VM diverge da cópia local → deploy por **patch idempotente com backup** (sem copiar
  arquivos inteiros), seguindo `sistema-gestor-vm-ops.md`.
- Nenhuma migração/backup de dados necessária.

## Anexo — Descobertas da implementação (bug fixes no importador de Produtos)
Durante os testes de aceite (CA5) foram encontrados **2 bugs latentes no importador
existente** (`estoque/views.py` `ProdutoImportView.save_produto`), corrigidos nesta
entrega porque bloqueavam o uso correto do modelo:
1. **Movimentação inicial sem `empresa`**: `MovimentacaoEstoque.save()` chama
   `full_clean()` (empresa obrigatória) → importar produto com `estoque_inicial > 0`
   criava o produto e setava o estoque, mas **falhava ao registrar a movimentação**
   ("Linha 1: {'empresa': ['Este campo não pode estar vazio.']}"). Além disso, o
   `save()` do modelo **já aplica o efeito no estoque automaticamente** — setar
   `estoque.quantidade` manualmente antes duplicaria a contagem. Fix: criar a
   movimentação com `empresa=empresa` e deixar o modelo aplicar o saldo.
2. **Categoria vazia criava categoria `''`**: `row.get('categoria', 'Geral')` não
   aplica o default quando a coluna existe mas está vazia. Fix:
   `row.get('categoria') or 'Geral'`.

---

## Fluxo de trabalho (Spec → Implementa → Verifica)
1. **Escrever a spec** (este arquivo, num branch `feature/xxxx`).
2. **Revisar** comigo (Hermes): clareza, critérios de aceite testáveis, não-escopo.
3. **Implementar** (IA com método + TDD) contra a spec.
4. **Verificar**: `pytest` (critérios de aceite viram testes) + `hermes verify --json`.
5. **Deploy** (VM) com backup → **validar ao vivo**.
6. **Fechar** a spec (status `implementado`) e arquivar.