from datetime import date
from celery import shared_task
from django.apps import apps

from meigestao_app.core.models import Empresa

from .services import CientistaFinanceiroService


def _get_relatorio_inteligencia_model():
    try:
        return apps.get_model('financeiro', 'RelatorioInteligencia')
    except LookupError as exc:
        raise RuntimeError(
            'Modelo financeiro.RelatorioInteligencia nao encontrado. '
            'A tarefa nao pode prosseguir sem persistencia duravel.'
        ) from exc


@shared_task
def processar_bi_financeiro_noturno():
    empresas = Empresa.objects.filter(ativa=True)
    relatorio_model = _get_relatorio_inteligencia_model()

    for empresa in empresas:
        analise = CientistaFinanceiroService.gerar_analise_matinal(empresa)

        relatorio_model.objects.update_or_create(
            empresa=empresa,
            data_referencia=date.today(),
            defaults={'dados_json': analise},
        )

    return f'Processado para {empresas.count()} empresas.'
