# BASELINE DA CÓPIA DE CORREÇÃO

Data de criação: 2026-08-12

## Origem preservada

- Pacote original: `../sistema-gestor.zip`
- SHA-256: `4874173bad8e077f1126729e8016d66676fba526774fe724f18ba46b0357d643`
- Cópia somente leitura: `../projeto-somente-leitura`

## Itens intencionalmente não copiados

- `.env` e arquivo `.env` vazio com nome incorreto;
- `db.sqlite3` e backup do banco;
- `media/`;
- `Arquivo_Morto/`;
- configurações da IDE;
- instalador `Verdent-2.2.5-Windows-x64.exe`;
- arquivo compactado interno `MANUAL PDF.rar`;
- arquivos `.backup` e `desktop.ini`.

Esses itens permanecem preservados na cópia somente leitura, mas não pertencem à base limpa de correção.

## Ajustes de higiene realizados antes do baseline

- criação de `.gitignore`;
- sanitização dos exemplos de senha e chave em `.env.example`;
- inicialização de repositório Git local.

## Estado técnico conhecido

Este commit representa uma base de trabalho, não uma versão aprovada para produção. A auditoria já identificou falhas que serão corrigidas por TDD em commits posteriores. A compilação sintática encontrou um erro preexistente em `scripts/gerar_views_relatorios.py:208`; ele foi mantido para correção rastreável posterior.

Nenhuma alteração foi enviada ao GitHub ou à VM Oracle.
