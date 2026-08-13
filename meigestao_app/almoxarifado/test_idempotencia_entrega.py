from datetime import date
from decimal import Decimal

import pytest
from django.contrib.auth.models import User

from meigestao_app.almoxarifado.models import (
    ItemRequisicao,
    LocalArmazenamento,
    RequisicaoInterna,
    SaldoAlmoxarifado,
    Setor,
)
from meigestao_app.core.models import Empresa
from meigestao_app.estoque.models import Categoria, Produto
from meigestao_app.usuarios.models import Perfil


@pytest.mark.django_db
def test_salvar_requisicao_entregue_novamente_nao_desconta_saldo_duas_vezes():
    empresa = Empresa.objects.create(nome="Idempotência", cnpj="91.111.111/0001-91")
    usuario = User.objects.create_user(username="idempotencia", password="teste-forte")
    Perfil.objects.create(
        usuario=usuario,
        empresa=empresa,
        data_admissao=date.today(),
    )
    categoria = Categoria.objects.create(empresa=empresa, nome="Materiais")
    produto = Produto.objects.create(
        empresa=empresa,
        categoria=categoria,
        nome="Material",
        sku="IDEMP-001",
        preco_custo="1.00",
        preco_venda="2.00",
    )
    local = LocalArmazenamento.objects.create(empresa=empresa, nome="Depósito")
    setor = Setor.objects.create(empresa=empresa, nome="Produção")
    saldo = SaldoAlmoxarifado.objects.create(
        local=local,
        produto=produto,
        quantidade=Decimal("10.00"),
    )
    requisicao = RequisicaoInterna.objects.create(
        empresa=empresa,
        solicitante=usuario,
        setor=setor,
        local_origem=local,
        justificativa="Teste de idempotência",
    )
    ItemRequisicao.objects.create(
        requisicao=requisicao,
        produto=produto,
        quantidade_solicitada=Decimal("2.00"),
        quantidade_entregue=Decimal("2.00"),
    )

    requisicao.status = "ENTREGUE"
    requisicao.save()
    saldo.refresh_from_db()
    assert saldo.quantidade == Decimal("8.00")

    requisicao.save()
    saldo.refresh_from_db()

    assert saldo.quantidade == Decimal("8.00")
