from decimal import Decimal
import threading

import pytest
from django.db import close_old_connections, connection

from meigestao_app.clientes.models import Cliente
from meigestao_app.core.models import Empresa
from meigestao_app.fiscal.models import NotaFiscal


@pytest.fixture
def base_fiscal(db):
    empresa_a = Empresa.objects.create(nome='Empresa Fiscal A', cnpj='40.111.111/0001-40')
    empresa_b = Empresa.objects.create(nome='Empresa Fiscal B', cnpj='41.222.222/0001-41')
    cliente_a = Cliente.objects.create(
        empresa=empresa_a,
        nome='Cliente Fiscal A',
        cpf_cnpj='401.111.111-40',
    )
    cliente_b = Cliente.objects.create(
        empresa=empresa_b,
        nome='Cliente Fiscal B',
        cpf_cnpj='412.222.222-41',
    )
    return empresa_a, empresa_b, cliente_a, cliente_b


@pytest.mark.django_db
def test_emitir_nota_gera_numero_sequencial_por_empresa_serie(base_fiscal):
    empresa_a, _, cliente_a, _ = base_fiscal
    nf1 = NotaFiscal.objects.create(
        empresa=empresa_a,
        cliente=cliente_a,
        serie='1',
        valor_subtotal=Decimal('100.00'),
    )
    nf2 = NotaFiscal.objects.create(
        empresa=empresa_a,
        cliente=cliente_a,
        serie='1',
        valor_subtotal=Decimal('200.00'),
    )

    nf1.emitir()
    nf2.emitir()

    nf1.refresh_from_db()
    nf2.refresh_from_db()
    assert nf1.status == 'emitida'
    assert nf2.status == 'emitida'
    assert nf1.numero == '1'
    assert nf2.numero == '2'


@pytest.mark.django_db
def test_sequencia_reinicia_por_serie_e_empresa(base_fiscal):
    empresa_a, empresa_b, cliente_a, cliente_b = base_fiscal
    nf_a_serie_1 = NotaFiscal.objects.create(
        empresa=empresa_a,
        cliente=cliente_a,
        serie='1',
        valor_subtotal=Decimal('100.00'),
    )
    nf_a_serie_2 = NotaFiscal.objects.create(
        empresa=empresa_a,
        cliente=cliente_a,
        serie='2',
        valor_subtotal=Decimal('100.00'),
    )
    nf_b_serie_1 = NotaFiscal.objects.create(
        empresa=empresa_b,
        cliente=cliente_b,
        serie='1',
        valor_subtotal=Decimal('100.00'),
    )

    nf_a_serie_1.emitir()
    nf_a_serie_2.emitir()
    nf_b_serie_1.emitir()

    nf_a_serie_1.refresh_from_db()
    nf_a_serie_2.refresh_from_db()
    nf_b_serie_1.refresh_from_db()

    assert nf_a_serie_1.numero == '1'
    assert nf_a_serie_2.numero == '1'
    assert nf_b_serie_1.numero == '1'


@pytest.mark.django_db(transaction=True)
def test_emitir_nota_concorrente_gera_numeros_distintos_no_postgresql(base_fiscal):
    if connection.vendor != 'postgresql':
        pytest.skip('Teste concorrente específico de lock no PostgreSQL')

    empresa_a, _, cliente_a, _ = base_fiscal
    nf1 = NotaFiscal.objects.create(
        empresa=empresa_a,
        cliente=cliente_a,
        serie='1',
        valor_subtotal=Decimal('100.00'),
    )
    nf2 = NotaFiscal.objects.create(
        empresa=empresa_a,
        cliente=cliente_a,
        serie='1',
        valor_subtotal=Decimal('200.00'),
    )

    erros = []
    barreira = threading.Barrier(2)

    def worker(nota_id):
        close_old_connections()
        try:
            nota = NotaFiscal.objects.get(pk=nota_id)
            barreira.wait(timeout=5)
            nota.emitir()
        except Exception as exc:  # pragma: no cover - audit probe
            erros.append(type(exc).__name__)
        finally:
            close_old_connections()

    t1 = threading.Thread(target=worker, args=(nf1.pk,), daemon=True)
    t2 = threading.Thread(target=worker, args=(nf2.pk,), daemon=True)
    t1.start()
    t2.start()
    t1.join(timeout=10)
    t2.join(timeout=10)

    assert not t1.is_alive()
    assert not t2.is_alive()
    assert erros == []

    nf1.refresh_from_db()
    nf2.refresh_from_db()
    assert nf1.status == 'emitida'
    assert nf2.status == 'emitida'
    assert {nf1.numero, nf2.numero} == {'1', '2'}
