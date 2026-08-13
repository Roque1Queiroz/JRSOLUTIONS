from django.test import TestCase
from datetime import date
from meigestao_app.core.models import Empresa
from meigestao_app.financeiro.models import Transacao, ContaBancaria
from meigestao_app.financeiro.services import CientistaFinanceiroService

class TestInteligenciaFinanceira(TestCase):
    def setUp(self):
        self.empresa = Empresa.objects.create(nome="Roque Solutions",)
        # Usando ContaBancaria em vez de Caixa
        self.conta = ContaBancaria.objects.create(
            empresa=self.empresa, 
            banco="Banco do Brasil",
            agencia="1234",
            conta="56789",
            saldo=1000.00
        )

    def test_projecao_financeira_positiva(self):
        Transacao.objects.create(
            empresa=self.empresa, 
            tipo='receita', 
            valor=500.00, 
            data_vencimento=date.today(),
            data_transacao=date.today(),
            categoria="Vendas"
        )
        
        analise = CientistaFinanceiroService.gerar_analise_matinal(self.empresa)
        self.assertEqual(analise['projecao'], 1500.00)
        self.assertEqual(analise['status'], 'SUCESSO')

    def test_alerta_saldo_negativo(self):
        Transacao.objects.create(
            empresa=self.empresa, 
            tipo='despesa', 
            valor=1500.00, 
            data_vencimento=date.today(),
            data_transacao=date.today(),
            categoria="Fornecedores"
        )
        
        analise = CientistaFinanceiroService.gerar_analise_matinal(self.empresa)
        self.assertLess(analise['projecao'], 0)
        self.assertEqual(analise['status'], 'PERIGO')