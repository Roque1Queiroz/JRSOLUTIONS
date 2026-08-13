from celery import shared_task
from meigestao_app.core.models import Empresa
from .services import CientistaFinanceiroService
from .models import RelatorioInteligencia # Model para salvar o resultado

@shared_task
def processar_bi_financeiro_noturno():
    empresas = Empresa.objects.filter(ativo=True)
    for empresa in empresas:
        analise = CientistaFinanceiroService.gerar_analise_matinal(empresa)
        
        # Salva para o gerente ler as 09:00
        RelatorioInteligencia.objects.update_or_create(
            empresa=empresa,
            data_referencia=date.today(),
            defaults={'dados_json': analise}
        )
    return f"Processado para {empresas.count()} empresas."