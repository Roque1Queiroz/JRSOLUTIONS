from unittest.mock import patch

from django.test import TestCase

from meigestao_app.core.models import Empresa
from meigestao_app.financeiro.tasks import processar_bi_financeiro_noturno


class TestFinanceiroTasks(TestCase):
    def test_task_falha_se_modelo_relatorio_nao_existir(self):
        ativa = Empresa.objects.create(nome='Empresa Ativa', cnpj='00.000.000/0001-01')
        Empresa.objects.create(nome='Empresa Inativa', cnpj='00.000.000/0001-02', ativa=False)

        with patch(
            'meigestao_app.financeiro.tasks.CientistaFinanceiroService.gerar_analise_matinal',
            return_value={
                'data': '14/08/2026',
                'entradas_hoje': 0.0,
                'saidas_hoje': 0.0,
                'projecao': 0.0,
                'status': 'SUCESSO',
                'mensagem': 'ok',
            },
        ) as mock_service:
            with self.assertRaisesRegex(RuntimeError, 'RelatorioInteligencia'):
                processar_bi_financeiro_noturno()

        mock_service.assert_not_called()
