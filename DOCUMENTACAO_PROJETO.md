# **SISTEMA GESTOR (PME/SaaS)* - DOCUMENTAÇÃO DO PROJETO

## Status: ✅ FUNCIONAL

### Estrutura do Projeto
- meigestao_app/
  - core/        (Dashboard, Empresa)
  - vendas/      (Vendas, ItemVenda)
  - clientes/    (Clientes)
  - estoque/     (Produtos, Estoque)
  - financeiro/  (Transações, Fluxo de Caixa)
  - fiscal/      (Notas Fiscais)
  - usuarios/    (Usuários)

### Como Rodar o Servidor
1. Ativar venv: .env\Scripts\Activate.ps1
2. Rodar servidor: python manage.py runserver
3. Acessar: http://127.0.0.1:8000/

### Banco de Dados
- Tipo: SQLite (db.sqlite3)
- Migrações: python manage.py migrate
- Criar superuser: python manage.py createsuperuser

### Próximos Passos
1. ✅ Restauração concluída
2. ⏳ Implementar templates para todos os módulos
3. ⏳ Adicionar testes unitários
4. ⏳ Configurar CI/CD
5. ⏳ Deploy em produção

### Contato/Suporte
Arquiteto de Software Sênior - Full-Stack Expert
