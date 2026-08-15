from unittest.mock import patch

from django.test import TestCase

from meigestao_app.core.models import Empresa
from meigestao_app.financeiro.models import RelatorioInteligencia
from meigestao_app.financeiro.tasks import processar_bi_financeiro_noturno


ANALISE_RETORNO = {
    'data': '14/08/2026',
    'entradas_hoje': 150.0,
    'saidas_hoje': 50.0,
    'projecao': 100.0,
    'status': 'SUCESSO',
    'mensagem': 'Saúde financeira estável.',
}


def _cria_empresa(nome, cnpj, ativa=True):
    return Empresa.objects.create(nome=nome, cnpj=cnpj, ativa=ativa)


class TestFinanceiroTasks(TestCase):
    def test_task_falha_se_modelo_relatorio_nao_existir(self):
        _cria_empresa('Empresa Ativa', '00.000.000/0001-01')
        _cria_empresa('Empresa Inativa', '00.000.000/0001-02', ativa=False)

        with patch(
            'meigestao_app.financeiro.tasks.apps.get_model',
            side_effect=LookupError('modelo ausente'),
        ), patch(
            'meigestao_app.financeiro.tasks.CientistaFinanceiroService.gerar_analise_matinal'
        ) as mock_service:
            with self.assertRaisesRegex(RuntimeError, 'RelatorioInteligencia'):
                processar_bi_financeiro_noturno()

        mock_service.assert_not_called()

    def test_task_persiste_relatorio_por_empresa_ativa(self):
        _cria_empresa('Empresa Ativa', '00.000.000/0001-01')
        _cria_empresa('Empresa Inativa', '00.000.000/0001-02', ativa=False)

        with patch(
            'meigestao_app.financeiro.tasks.CientistaFinanceiroService.gerar_analise_matinal',
            return_value=ANALISE_RETORNO,
        ):
            processar_bi_financeiro_noturno()

        relatorios = RelatorioInteligencia.objects.all()
        self.assertEqual(relatorios.count(), 1)
        rel = relatorios.get()
        self.assertEqual(rel.dados_json, ANALISE_RETORNO)
