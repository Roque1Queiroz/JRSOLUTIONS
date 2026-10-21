# Spec — Etiqueta limpa da peça (QR do almoxarifado)

| Campo | Valor |
|---|---|
| **Versão** | 1.0 |
| **Status** | aprovado — na fila, ainda não implementar |
| **Autor** | José Roque / Hermes |
| **Data** | 2026-10-09 |
| **Módulos afetados** | almoxarifado |
| **Plano** | profissional e enterprise (o básico já bloqueia o almoxarifado) |

DECISÃO (José, ok em 2026-10-09): na caixa da peça só um QR pequeno e o código. O resto aparece na tela ao apontar o celular. A prateleira continua como está. Fechar a spec e colocar na fila. Não codar até ele mandar executar a fila.

---

## 1. Objetivo (por que?)

A caixa da peça não pode levar nome, local e quantidade impressos. Isso polui e fica velho. Um QR pequeno guarda só o código. Quem aponta a câmera vê a ficha atualizada no sistema.

## 2. Contexto / Cenário atual

Inspecionado em `meigestao_app/almoxarifado/` em 2026-10-09:

- **Central de Etiquetas** (`/almoxarifado/etiquetas/`) já gera duas coisas no navegador, com `qrcodejs` e `JsBarcode`.
- Etiqueta de prateleira: QR com a URL `/almoxarifado/p/<codigo_endereco>/`. A leitura abre `PrateleiraView`, com local e saldos. Isso fica como está.
- Etiqueta de produto: código de barras Code 128 só com o SKU, e ao lado ainda imprime nome, endereço e SKU. Não abre ficha. A caixa continua poluída.
- O admin do Django ainda chama sites externos (`api.qrserver.com` e `barcode.tec-it.com`) para o endereço. Isso não é o fluxo do operador e não entra nesta spec.
- `Produto.sku` é único. `SaldoAlmoxarifado` liga produto, local, endereço, quantidade e quantidade mínima.
- Plano básico não entra no almoxarifado (`core/middleware.py`).

## 3. Escopo

- **Incluído:**
  - Etiqueta da peça só com QR e o código (SKU). Sem nome, sem endereço, sem quantidade impressos.
  - O QR guarda somente a URL da ficha da peça.
  - Ficha ao escanear: nome, código, cada local/endereço, saldo e mínimo. Dados lidos na hora, não gravados no QR.
  - Escolher quais peças imprimir, em vez de sair a lista inteira de uma vez.
  - A etiqueta de prateleira que já existe permanece.
- **Excluído (não-escopo):**
  - Enfiar texto longo dentro das barras. Código de barras Code 128 não cabe ficha e aumenta a etiqueta.
  - Gravar quantidade, preço ou nome dentro do QR.
  - Trocar o QR da prateleira.
  - Tirar o QR/código de barras do admin Django.
  - Leitura sem login.
  - Pacote de textos e nosso boleto.

## 4. Requisitos Funcionais (o que o sistema FAZ)

- RF1 — Na Central de Etiquetas, a etiqueta da peça mostra só o QR e o SKU.
- RF2 — O texto do QR é a URL da ficha daquela peça, no mesmo site. Não leva nome nem quantidade.
- RF3 — Quem abre essa URL, já logado e com acesso ao almoxarifado, vê a ficha: nome, SKU, locais, endereços, saldo e mínimo.
- RF4 — A ficha lista todos os saldos daquela peça na empresa do usuário.
- RF5 — Dá para marcar quais peças imprimir. Imprimir não despeja nome na etiqueta.
- RF6 — A etiqueta e a rota da prateleira (`/almoxarifado/p/<codigo>/`) continuam iguais.

## 5. Requisitos Não-Funcionais

- O QR é gerado no navegador, com a biblioteca que a Central já usa. Sem chamar site externo para desenhar o código da peça.
- Isolamento por empresa na ficha.
- A etiqueta impressa cabe numa caixa: QR pequeno e o código. Sem parágrafo.
- Login obrigatório na ficha, no mesmo padrão da prateleira.

## 6. Dados / Modelo

Nenhum modelo novo. Nenhum campo novo.

A URL prevista é `/almoxarifado/peca/<sku>/`. O SKU vai codificado na URL. A view busca o produto por SKU e os saldos pela empresa do usuário.

O QR não é um documento. Se o saldo mudar, a próxima leitura já mostra o número novo.

## 7. Fluxo / Telas

1. Almoxarifado → Central de Etiquetas.
2. Na parte da peça, marca as caixas que vai etiquetar.
3. Imprime. Sai QR + código.
4. No chão, aponta a câmera. Abre a ficha, se a pessoa estiver logada no sistema.

Rotas:

- `etiquetas/` — já existe; a parte da peça muda.
- `peca/<sku>/` — ficha nova. Nome previsto: `peca_view`.

## 8. Segurança / Restrições por Plano e Empresa

- A ficha filtra saldo pela empresa do usuário. Peça de outra empresa não aparece.
- Mesma permissão de ver o almoxarifado. Quem não vê o módulo não abre a ficha.
- Plano básico continua bloqueado pelo middleware, porque a rota fica no namespace `almoxarifado`.
- Sem login, a ficha redireciona para o login. Não é página pública.

## 9. Critérios de Aceite (TESTES — o "check")

- CA1 — A etiqueta da peça, no HTML da Central, contém o SKU e a URL `/almoxarifado/peca/`, e o bloco impresso da peça não contém o nome do produto.
- CA2 — `GET /almoxarifado/peca/<sku>/` do usuário da empresa mostra nome, local, saldo e mínimo.
- CA3 — Usuário de outra empresa, no mesmo SKU, não vê saldo da empresa alheia.
- CA4 — Anônimo em `peca/<sku>/` não recebe a ficha (redirect para login).
- CA5 — A URL da prateleira continua respondendo como hoje.
- CA6 — A suíte do almoxarifado que já existe continua verde.

## 10. Riscos / Dependências

- A Central hoje baixa `qrcodejs` de um CDN. Sem internet no PC que imprime, o QR não desenha. Não trocar isso nesta leva. Se o chão for offline, fica para uma leva seguinte, gerando o QR no servidor.
- SKU com espaço ou barra precisa ir codificado na URL. A view tem que achar o mesmo SKU.
- Implementar só quando José mandar executar a fila. Branch `feature/etiqueta-limpa-peca`, um teste por critério, depois o código mínimo.

---

## Fluxo de trabalho

1. Spec escrita e aprovada em 2026-10-09.
2. Na fila: `docs/SPECS/FILA-ATUALIZACOES.md`, item 2.
3. Implementar só sob ordem, com TDD contra os CA.
4. Verificar, deploy com backup, validar ao vivo, então marcar esta spec como `implementado`.
