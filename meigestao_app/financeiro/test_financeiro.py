import pytest
from decimal import Decimal
from django.urls import reverse
from django.utils import timezone
from meigestao_app.financeiro.models import Transacao, ReciboReembolso, ContaBancaria
from meigestao_app.core.models import Empresa
from meigestao_app.core.context_processors import notifications
from meigestao_app.usuarios.models import Perfil
from meigestao_app.clientes.models import Cliente
from meigestao_app.estoque.models import Categoria, Produto, Estoque
from meigestao_app.vendas.models import Venda
from django.contrib.auth.models import User
from datetime import date
from django.test import RequestFactory

@pytest.fixture
def finance_data(db):
    empresa = Empresa.objects.create(nome="MEI Teste", cnpj="12.345.678/0001-99")
    user = User.objects.create_user(username="colab", password="password", is_staff=True)
    perfil = Perfil.objects.create(usuario=user, empresa=empresa, data_admissao=date.today())
    
    conta1 = ContaBancaria.objects.create(empresa=empresa, banco="Banco A", saldo=1000.00)
    conta2 = ContaBancaria.objects.create(empresa=empresa, banco="Banco B", saldo=500.00)
    
    reembolso = ReciboReembolso.objects.create(
        empresa=empresa,
        colaborador=perfil,
        item="Gasolina",
        valor=100.00,
        data_compra=timezone.now().date()
    )
    
    return {
        'empresa': empresa,
        'user': user,
        'conta1': conta1,
        'conta2': conta2,
        'reembolso': reembolso
    }

@pytest.mark.django_db
class TestFinanceiroFlow:
    """Testa o fluxo financeiro e integração de reembolsos."""

    def test_reembolso_payment_with_account_selection(self, client, finance_data):
        # Login
        client.login(username="colab", password="password")
        
        reembolso = finance_data['reembolso']
        conta = finance_data['conta2'] # Banco B (Saldo: 500)
        
        # Simular POST para pagar o reembolso escolhendo a conta 2
        url = reverse('financeiro:reembolso_pago', kwargs={'pk': reembolso.pk})
        response = client.post(url, {'conta_id': conta.id})
        
        # Verificar Redirecionamento
        assert response.status_code == 302
        
        # Recarregar Dados
        reembolso.refresh_from_db()
        conta.refresh_from_db()
        
        # Asserts
        assert reembolso.pago is True
        assert reembolso.transacao is not None
        assert reembolso.transacao.conta == conta
        assert reembolso.transacao.valor == Decimal('100.00')
        assert conta.saldo == Decimal('400.00') # 500 - 100
        
    def test_reembolso_reversal(self, client, finance_data):
        client.login(username="colab", password="password")
        reembolso = finance_data['reembolso']
        conta = finance_data['conta1']
        
        # Pagar primeiro
        client.post(reverse('financeiro:reembolso_pago', kwargs={'pk': reembolso.pk}), {'conta_id': conta.id})
        reembolso.refresh_from_db()
        conta.refresh_from_db()
        assert conta.saldo == Decimal('900.00')
        
        # Agora Estornar (mesmo endpoint alterna status)
        client.post(reverse('financeiro:reembolso_pago', kwargs={'pk': reembolso.pk}))
        
        reembolso.refresh_from_db()
        conta.refresh_from_db()
        
        assert reembolso.pago is False
        assert reembolso.transacao is None
        assert conta.saldo == Decimal('1000.00') # Saldo estornado

    def test_create_paid_expense_updates_account_balance(self, client, finance_data):
        client.login(username="colab", password="password")
        conta = finance_data['conta1']
        empresa = finance_data['empresa']

        response = client.post(reverse('financeiro:transacao_criar'), {
            'empresa': empresa.id,
            'conta': conta.id,
            'tipo': 'despesa',
            'categoria': 'Operacional',
            'descricao': 'Compra de materiais',
            'valor': '150.00',
            'data_transacao': '2026-04-14',
            'data_vencimento': '',
            'paga': 'on',
        })

        assert response.status_code == 302
        conta.refresh_from_db()
        transacao = Transacao.objects.get(descricao='Compra de materiais')

        assert transacao.paga is True
        assert conta.saldo == Decimal('850.00')

    def test_update_paid_expense_recalculates_account_balance(self, client, finance_data):
        client.login(username="colab", password="password")
        conta = finance_data['conta1']
        empresa = finance_data['empresa']
        transacao = Transacao.objects.create(
            empresa=empresa,
            conta=conta,
            tipo='despesa',
            categoria='Operacional',
            descricao='Internet',
            valor=100.00,
            data_transacao=timezone.now().date(),
            paga=True,
        )
        conta.saldo = Decimal('900.00')
        conta.save(update_fields=['saldo'])

        response = client.post(reverse('financeiro:transacao_editar', kwargs={'pk': transacao.pk}), {
            'empresa': empresa.id,
            'conta': conta.id,
            'tipo': 'despesa',
            'categoria': 'Operacional',
            'descricao': 'Internet atualizada',
            'valor': '250.00',
            'data_transacao': '2026-04-14',
            'data_vencimento': '',
            'paga': 'on',
        })

        assert response.status_code == 302
        conta.refresh_from_db()
        transacao.refresh_from_db()

        assert transacao.descricao == 'Internet atualizada'
        assert transacao.valor == Decimal('250.00')
        assert conta.saldo == Decimal('750.00')

    def test_report_generation_flow(self, client, finance_data):
        client.login(username="colab", password="password")
        empresa = finance_data['empresa']
        conta = finance_data['conta1']

        Transacao.objects.create(
            empresa=empresa,
            conta=conta,
            tipo='receita',
            categoria='Vendas',
            descricao='Venda teste',
            valor=500.00,
            data_transacao=date(2026, 4, 10),
            paga=True,
        )
        Transacao.objects.create(
            empresa=empresa,
            conta=conta,
            tipo='despesa',
            categoria='Custos',
            descricao='Despesa teste',
            valor=120.00,
            data_transacao=date(2026, 4, 11),
            paga=True,
        )

        response = client.post(reverse('financeiro:relatorio_criar'), {
            'empresa': empresa.id,
            'titulo': 'Fechamento Abril',
            'periodo': 'mensal',
            'data_inicio': '2026-04-01',
            'data_fim': '2026-04-30',
        })

        assert response.status_code == 302
        assert 'relatorios/' in response.url

        follow = client.get(response.url)
        assert follow.status_code == 200
        assert len(follow.context['relatorios']) == 1

        relatorio = follow.context['relatorios'][0]
        assert relatorio.titulo == 'Fechamento Abril'
        assert relatorio.total_receitas == Decimal('500')
        assert relatorio.total_despesas == Decimal('120')
        assert relatorio.saldo_liquido == Decimal('380')

    def test_reembolso_insufficient_funds_does_not_create_transaction(self, client, finance_data):
        client.login(username="colab", password="password")
        reembolso = finance_data['reembolso']
        conta = finance_data['conta2']
        conta.saldo = Decimal('50.00')
        conta.save(update_fields=['saldo'])

        response = client.post(reverse('financeiro:reembolso_pago', kwargs={'pk': reembolso.pk}), {
            'conta_id': conta.id
        })

        assert response.status_code == 302
        reembolso.refresh_from_db()
        conta.refresh_from_db()

        assert reembolso.pago is False
        assert reembolso.transacao is None
        assert conta.saldo == Decimal('50.00')
        assert Transacao.objects.filter(descricao__icontains='Gasolina').count() == 0

    def test_non_staff_cannot_toggle_reembolso_payment(self, client, db):
        empresa = Empresa.objects.create(nome="MEI Bloqueio", cnpj="98.765.432/0001-11")
        user = User.objects.create_user(username="operador", password="password", is_staff=False)
        perfil = Perfil.objects.create(usuario=user, empresa=empresa, data_admissao=date.today())
        reembolso = ReciboReembolso.objects.create(
            empresa=empresa,
            colaborador=perfil,
            item="Taxi",
            valor=50.00,
            data_compra=timezone.now().date()
        )

        client.login(username="operador", password="password")
        response = client.post(reverse('financeiro:reembolso_pago', kwargs={'pk': reembolso.pk}))

        assert response.status_code == 403

    def test_linked_reimbursement_transaction_cannot_be_edited(self, client, finance_data):
        client.login(username="colab", password="password")
        reembolso = finance_data['reembolso']
        conta = finance_data['conta1']
        client.post(reverse('financeiro:reembolso_pago', kwargs={'pk': reembolso.pk}), {'conta_id': conta.id})
        reembolso.refresh_from_db()

        response = client.post(reverse('financeiro:transacao_editar', kwargs={'pk': reembolso.transacao.pk}), {
            'empresa': finance_data['empresa'].id,
            'conta': conta.id,
            'tipo': 'despesa',
            'categoria': 'Operacional',
            'descricao': 'Tentativa de editar',
            'valor': '90.00',
            'data_transacao': '2026-04-14',
            'data_vencimento': '',
            'paga': 'on',
        })

        assert response.status_code == 302
        reembolso.transacao.refresh_from_db()
        assert 'Tentativa de editar' not in reembolso.transacao.descricao

    def test_receita_list_route_filters_only_receitas(self, client, finance_data):
        client.login(username="colab", password="password")
        empresa = finance_data['empresa']
        conta = finance_data['conta1']

        receita = Transacao.objects.create(
            empresa=empresa,
            conta=conta,
            tipo='receita',
            categoria='Serviços',
            descricao='Consultoria',
            valor=300.00,
            data_transacao=date(2026, 4, 12),
            paga=True,
        )
        Transacao.objects.create(
            empresa=empresa,
            conta=conta,
            tipo='despesa',
            categoria='Operacional',
            descricao='Energia',
            valor=90.00,
            data_transacao=date(2026, 4, 12),
            paga=True,
        )

        response = client.get(reverse('financeiro:receita_lista'))

        assert response.status_code == 200
        transacoes = list(response.context['transacoes'])
        assert transacoes == [receita]
        assert response.context['flow_page_title'] == 'Receitas'

    def test_create_receita_dedicated_flow_forces_tipo_and_updates_balance(self, client, finance_data):
        client.login(username="colab", password="password")
        conta = finance_data['conta1']
        empresa = finance_data['empresa']

        form_response = client.get(reverse('financeiro:receita_criar'))
        assert form_response.status_code == 200
        assert b'name="tipo"' not in form_response.content

        response = client.post(reverse('financeiro:receita_criar'), {
            'empresa': empresa.id,
            'conta': conta.id,
            'tipo': 'despesa',
            'categoria': 'Serviços',
            'descricao': 'Projeto fechado',
            'valor': '250.00',
            'data_transacao': '2026-04-14',
            'data_vencimento': '',
            'paga': 'on',
        })

        assert response.status_code == 302
        conta.refresh_from_db()
        receita = Transacao.objects.get(descricao='Projeto fechado')

        assert receita.tipo == 'receita'
        assert conta.saldo == Decimal('1250.00')

    def test_receita_detail_and_update_routes_only_accept_receitas(self, client, finance_data):
        client.login(username="colab", password="password")
        empresa = finance_data['empresa']
        conta = finance_data['conta1']

        receita = Transacao.objects.create(
            empresa=empresa,
            conta=conta,
            tipo='receita',
            categoria='Serviços',
            descricao='Mensalidade',
            valor=120.00,
            data_transacao=date(2026, 4, 13),
            paga=False,
        )
        despesa = Transacao.objects.create(
            empresa=empresa,
            conta=conta,
            tipo='despesa',
            categoria='Operacional',
            descricao='Internet',
            valor=80.00,
            data_transacao=date(2026, 4, 13),
            paga=False,
        )

        detail_response = client.get(reverse('financeiro:receita_detalhe', kwargs={'pk': receita.pk}))
        blocked_response = client.get(reverse('financeiro:receita_detalhe', kwargs={'pk': despesa.pk}))

        assert detail_response.status_code == 200
        assert blocked_response.status_code == 404

        update_response = client.post(reverse('financeiro:receita_editar', kwargs={'pk': receita.pk}), {
            'empresa': empresa.id,
            'conta': conta.id,
            'tipo': 'despesa',
            'categoria': 'Serviços Recorrentes',
            'descricao': 'Mensalidade atualizada',
            'valor': '180.00',
            'data_transacao': '2026-04-14',
            'data_vencimento': '',
            'paga': '',
        })

        assert update_response.status_code == 302
        receita.refresh_from_db()

        assert receita.tipo == 'receita'
        assert receita.descricao == 'Mensalidade atualizada'
        assert receita.valor == Decimal('180.00')

    def test_dashboard_non_staff_is_scoped_to_user_company(self, client, db):
        empresa_a = Empresa.objects.create(nome="Empresa A", cnpj="11.111.111/0001-11")
        empresa_b = Empresa.objects.create(nome="Empresa B", cnpj="22.222.222/0001-22")

        user = User.objects.create_user(username="escopo", password="password", is_staff=False)
        Perfil.objects.create(usuario=user, empresa=empresa_a, data_admissao=date.today())

        cliente_a = Cliente.objects.create(empresa=empresa_a, nome="Cliente A", cpf_cnpj="111.111.111-11")
        cliente_b = Cliente.objects.create(empresa=empresa_b, nome="Cliente B", cpf_cnpj="222.222.222-22")

        categoria = Categoria.objects.create(nome="Serviços de Teste")
        produto_a = Produto.objects.create(empresa=empresa_a, categoria=categoria, nome="Produto A", sku="SKU-A", preco_custo=10, preco_venda=20)
        produto_b = Produto.objects.create(empresa=empresa_b, categoria=categoria, nome="Produto B", sku="SKU-B", preco_custo=10, preco_venda=20)

        Estoque.objects.create(produto=produto_a, quantidade=1, quantidade_minima=3)
        Estoque.objects.create(produto=produto_b, quantidade=1, quantidade_minima=3)

        ContaBancaria.objects.create(empresa=empresa_a, banco="Banco A", agencia="0001", conta="12345", saldo=150)
        ContaBancaria.objects.create(empresa=empresa_b, banco="Banco B", agencia="0001", conta="67890", saldo=900)

        Venda.objects.create(
            empresa=empresa_a,
            cliente=cliente_a,
            status='confirmada',
            valor_subtotal=200,
            valor_total=200,
            data_venda=timezone.now(),
        )
        Venda.objects.create(
            empresa=empresa_b,
            cliente=cliente_b,
            status='confirmada',
            valor_subtotal=500,
            valor_total=500,
            data_venda=timezone.now(),
        )

        colaborador_b = User.objects.create_user(username="colab_b", password="password")
        perfil_b = Perfil.objects.create(usuario=colaborador_b, empresa=empresa_b, data_admissao=date.today())
        ReciboReembolso.objects.create(
            empresa=empresa_a,
            colaborador=Perfil.objects.get(usuario=user),
            item="Taxi A",
            valor=50,
            data_compra=timezone.now().date(),
        )
        ReciboReembolso.objects.create(
            empresa=empresa_b,
            colaborador=perfil_b,
            item="Taxi B",
            valor=70,
            data_compra=timezone.now().date(),
        )

        client.login(username="escopo", password="password")
        response = client.get(reverse('core:dashboard'))

        assert response.status_code == 200
        assert response.context['total_clientes'] == 1
        assert response.context['total_produtos'] == 1
        assert response.context['total_vendas'] == 1
        assert response.context['saldo_caixa'] == Decimal('150')
        assert response.context['faturamento_mes'] == Decimal('200')
        assert response.context['estoque_baixo'] == 1
        assert response.context['reembolsos_pendentes_count'] == 1

    def test_staff_reembolso_create_uses_colaborador_empresa_without_fallback(self, client, db):
        empresa = Empresa.objects.create(nome="Empresa Staff", cnpj="33.333.333/0001-33")
        admin = User.objects.create_user(username="admin_fin", password="password", is_staff=True)
        colaborador_user = User.objects.create_user(username="func_fin", password="password")
        colaborador = Perfil.objects.create(usuario=colaborador_user, empresa=empresa, data_admissao=date.today())

        client.login(username="admin_fin", password="password")
        response = client.post(reverse('financeiro:reembolso_criar'), {
            'colaborador': colaborador.pk,
            'item': 'Hospedagem',
            'valor': '89.90',
            'data_compra': '2026-04-15',
            'observacoes': 'Teste admin sem perfil',
        })

        assert response.status_code == 302
        reembolso = ReciboReembolso.objects.get(item='Hospedagem')
        assert reembolso.empresa == empresa

    def test_usuario_sem_perfil_nao_cria_transacao_em_empresa_arbitraria(self, client, db):
        empresa = Empresa.objects.create(nome="Empresa Alvo", cnpj="44.444.444/0001-44")
        user = User.objects.create_user(username="sem_perfil_fin", password="password")
        client.login(username="sem_perfil_fin", password="password")

        response = client.post(reverse('financeiro:transacao_criar'), {
            'empresa': empresa.pk,
            'conta': '',
            'tipo': 'receita',
            'categoria': 'Indevida',
            'descricao': 'Tentativa sem vínculo empresarial',
            'valor': '100.00',
            'data_transacao': '2026-08-13',
            'data_vencimento': '',
            'paga': '',
        })

        assert response.status_code == 403
        assert not Transacao.objects.filter(
            descricao='Tentativa sem vínculo empresarial',
        ).exists()

    def test_usuario_com_perfil_so_pode_criar_transacao_na_propria_empresa(self, client, db):
        empresa_a = Empresa.objects.create(nome="Empresa A Segura", cnpj="66.666.666/0001-66")
        empresa_b = Empresa.objects.create(nome="Empresa B Alvo", cnpj="77.777.777/0001-77")
        user = User.objects.create_user(username="perfil_empresa_a", password="password")
        Perfil.objects.create(usuario=user, empresa=empresa_a, data_admissao=date.today())
        client.login(username="perfil_empresa_a", password="password")

        response = client.post(reverse('financeiro:transacao_criar'), {
            'empresa': empresa_b.pk,
            'conta': '',
            'tipo': 'receita',
            'categoria': 'Manipulada',
            'descricao': 'Tentativa em outra empresa',
            'valor': '100.00',
            'data_transacao': '2026-08-13',
            'data_vencimento': '',
            'paga': '',
        })

        assert response.status_code == 302
        assert Transacao.objects.filter(
            empresa=empresa_a,
            descricao='Tentativa em outra empresa',
        ).exists()
        assert not Transacao.objects.filter(
            empresa=empresa_b,
            descricao='Tentativa em outra empresa',
        ).exists()

    def test_perfil_inativo_nao_cria_transacao_financeira(self, client, db):
        empresa = Empresa.objects.create(nome="Empresa Inativa", cnpj="55.555.555/0001-55")
        user = User.objects.create_user(username="perfil_inativo_fin", password="password")
        Perfil.objects.create(
            usuario=user,
            empresa=empresa,
            data_admissao=date.today(),
            ativo=False,
        )
        client.login(username="perfil_inativo_fin", password="password")

        response = client.post(reverse('financeiro:transacao_criar'), {
            'empresa': empresa.pk,
            'conta': '',
            'tipo': 'receita',
            'categoria': 'Indevida',
            'descricao': 'Tentativa com perfil inativo',
            'valor': '100.00',
            'data_transacao': '2026-08-13',
            'data_vencimento': '',
            'paga': '',
        })

        assert response.status_code == 403
        assert not Transacao.objects.filter(
            descricao='Tentativa com perfil inativo',
        ).exists()

    def test_notifications_context_processor_returns_zero_for_user_without_profile(self, db):
        user = User.objects.create_user(username="semperfil", password="password", is_staff=False)
        request = RequestFactory().get('/')
        request.user = user

        context = notifications(request)

        assert context['reembolsos_pendentes_count'] == 0
