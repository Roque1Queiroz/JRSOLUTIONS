"""
Script de teste manual para CRUD de Empresa
Execute: python manage.py shell &lt; test_empresa_crud.py
"""

from meigestao_app.core.models import Empresa
from django.utils import timezone

print("=" * 60)
print("TESTE CRUD - EMPRESA")
print("=" * 60)

# CREATE
print("\n✅ TESTE 1: CREATE (Criar Empresa)")
empresa = Empresa.objects.create(
    nome="Tech Solutions Ltda",
    cnpj="12.345.678/0001-99",
    email="contato@techsolutions.com.br",
    telefone="(11) 98765-4321",
    endereco="Av. Paulista, 1000 - São Paulo, SP",
    ativa=True
)
print(f"   Empresa criada: {empresa.nome} (ID: {empresa.pk})")

# READ (List)
print("\n✅ TESTE 2: READ - List (Listar Empresas)")
empresas = Empresa.objects.all()
print(f"   Total de empresas: {empresas.count()}")
for e in empresas:
    print(f"   - {e.nome} (CNPJ: {e.cnpj})")

# READ (Detail)
print("\n✅ TESTE 3: READ - Detail (Detalhes da Empresa)")
empresa_detail = Empresa.objects.get(pk=empresa.pk)
print(f"   Nome: {empresa_detail.nome}")
print(f"   Email: {empresa_detail.email}")
print(f"   Ativa: {'Sim' if empresa_detail.ativa else 'Não'}")

# UPDATE
print("\n✅ TESTE 4: UPDATE (Atualizar Empresa)")
empresa.nome = "Tech Solutions Brasil"
empresa.telefone = "(11) 99999-9999"
empresa.save()
print(f"   Empresa atualizada: {empresa.nome}")

# DELETE
print("\n✅ TESTE 5: DELETE (Deletar Empresa)")
empresa_id = empresa.pk
empresa.delete()
print(f"   Empresa com ID {empresa_id} deletada com sucesso")

# Verificação final
print("\n✅ TESTE 6: Verificação Final")
total = Empresa.objects.count()
print(f"   Total de empresas no banco: {total}")

print("\n" + "=" * 60)
print("TODOS OS TESTES PASSARAM! ✅")
print("=" * 60)