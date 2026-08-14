import pytest
from django.core.exceptions import ValidationError
from django.db import DatabaseError, IntegrityError, transaction

from meigestao_app.clientes.models import Cliente
from meigestao_app.core.models import Empresa
from meigestao_app.fiscal.models import NotaFiscal
from meigestao_app.vendas.models import Venda


@pytest.fixture
def dados_fiscais_multitenant(db):
    empresa_a = Empresa.objects.create(nome="Fiscal Modelo A", cnpj="96.666.666/0001-96")
    empresa_b = Empresa.objects.create(nome="Fiscal Modelo B", cnpj="97.777.777/0001-97")
    cliente_a1 = Cliente.objects.create(
        empresa=empresa_a, nome="Cliente A1", cpf_cnpj="966.666.666-96"
    )
    cliente_a2 = Cliente.objects.create(
        empresa=empresa_a, nome="Cliente A2", cpf_cnpj="967.777.777-97"
    )
    cliente_b = Cliente.objects.create(
        empresa=empresa_b, nome="Cliente B", cpf_cnpj="977.777.777-97"
    )
    venda_a1 = Venda.objects.create(
        empresa=empresa_a,
        cliente=cliente_a1,
        valor_subtotal="100.00",
        valor_total="100.00",
    )
    return empresa_a, cliente_a1, cliente_a2, cliente_b, venda_a1


@pytest.mark.django_db
def test_nota_fiscal_rejeita_cliente_de_outra_empresa(dados_fiscais_multitenant):
    empresa_a, _, _, cliente_b, _ = dados_fiscais_multitenant
    nota = NotaFiscal(
        empresa=empresa_a,
        cliente=cliente_b,
        numero="NF-MODELO-01",
        valor_subtotal="100.00",
    )

    with pytest.raises(ValidationError) as erro:
        nota.full_clean()

    assert "cliente" in erro.value.message_dict


@pytest.mark.django_db
def test_nota_fiscal_rejeita_venda_de_outro_cliente(dados_fiscais_multitenant):
    empresa_a, _, cliente_a2, _, venda_a1 = dados_fiscais_multitenant
    nota = NotaFiscal(
        empresa=empresa_a,
        cliente=cliente_a2,
        venda=venda_a1,
        numero="NF-MODELO-02",
        valor_subtotal="100.00",
    )

    with pytest.raises(ValidationError) as erro:
        nota.full_clean()

    assert "venda" in erro.value.message_dict


@pytest.mark.django_db
def test_mesmo_numero_e_serie_podem_existir_em_empresas_diferentes(
    dados_fiscais_multitenant,
):
    empresa_a, cliente_a, _, cliente_b, _ = dados_fiscais_multitenant
    empresa_b = cliente_b.empresa

    NotaFiscal.objects.create(
        empresa=empresa_a,
        cliente=cliente_a,
        numero='1',
        serie='1',
        valor_subtotal='100.00',
    )
    nota_b = NotaFiscal.objects.create(
        empresa=empresa_b,
        cliente=cliente_b,
        numero='1',
        serie='1',
        valor_subtotal='100.00',
    )

    assert nota_b.pk is not None


@pytest.mark.django_db
def test_mesmo_numero_pode_existir_em_series_diferentes(
    dados_fiscais_multitenant,
):
    empresa_a, cliente_a, *_ = dados_fiscais_multitenant

    NotaFiscal.objects.create(
        empresa=empresa_a,
        cliente=cliente_a,
        numero='1',
        serie='1',
        valor_subtotal='100.00',
    )
    nota_serie_2 = NotaFiscal.objects.create(
        empresa=empresa_a,
        cliente=cliente_a,
        numero='1',
        serie='2',
        valor_subtotal='100.00',
    )

    assert nota_serie_2.pk is not None


@pytest.mark.django_db
def test_numero_e_serie_nao_se_repetem_na_mesma_empresa(
    dados_fiscais_multitenant,
):
    empresa_a, cliente_a, *_ = dados_fiscais_multitenant
    NotaFiscal.objects.create(
        empresa=empresa_a,
        cliente=cliente_a,
        numero='1',
        serie='1',
        valor_subtotal='100.00',
    )

    with pytest.raises((ValidationError, IntegrityError)):
        with transaction.atomic():
            NotaFiscal.objects.create(
                empresa=empresa_a,
                cliente=cliente_a,
                numero='1',
                serie='1',
                valor_subtotal='100.00',
            )


@pytest.mark.django_db
def test_queryset_update_nao_pode_emitir_sem_numero(dados_fiscais_multitenant):
    empresa_a, cliente_a1, *_ = dados_fiscais_multitenant
    nota = NotaFiscal.objects.create(
        empresa=empresa_a,
        cliente=cliente_a1,
        numero=None,
        serie='1',
        status='rascunho',
        valor_subtotal='100.00',
    )

    with pytest.raises(DatabaseError):
        with transaction.atomic():
            NotaFiscal.objects.filter(pk=nota.pk).update(status='emitida')

    nota.refresh_from_db()
    assert nota.status == 'rascunho'


@pytest.mark.django_db
def test_queryset_update_nao_pode_cancelar_sem_numero(dados_fiscais_multitenant):
    empresa_a, cliente_a1, *_ = dados_fiscais_multitenant
    nota = NotaFiscal.objects.create(
        empresa=empresa_a,
        cliente=cliente_a1,
        numero='',
        serie='1',
        status='rascunho',
        valor_subtotal='100.00',
    )

    with pytest.raises(DatabaseError):
        with transaction.atomic():
            NotaFiscal.objects.filter(pk=nota.pk).update(status='cancelada')

    nota.refresh_from_db()
    assert nota.status == 'rascunho'
