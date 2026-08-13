f = open('relatorios/views.py', 'w', encoding='utf-8')
f.write("""from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, View
from django.http import HttpResponse
from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum, Count, F
from django.db.models.functions import TruncMonth
from vendas.models import Venda, ItemVenda
from estoque.models import Produto
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
import io


def _get_vendas_filtradas(request):
    data_inicio = request.GET.get('data_inicio')
    data_fim    = request.GET.get('data_fim')
    status      = request.GET.get('status', 'confirmada')
    vendas = Venda.objects.select_related('cliente').prefetch_related('itens__produto')
    if status:
        vendas = vendas.filter(status=status)
    if data_inicio:
        vendas = vendas.filter(data_venda__date__gte=data_inicio)
    if data_fim:
        vendas = vendas.filter(data_venda__date__lte=data_fim)
    return vendas.order_by('-data_venda'), data_inicio, data_fim, status


class RelatoriosDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'relatorios/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        hoje = timezone.now()
        inicio_mes = hoje.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        vendas_mes = Venda.objects.filter(status='confirmada', data_venda__gte=inicio_mes).prefetch_related('itens')
        context['total_vendas_mes']  = vendas_mes.count()
        context['receita_mes']       = sum(v.total for v in vendas_mes)
        context['produtos_criticos'] = Produto.objects.filter(quantidade__lte=F('estoque_minimo')).count()
        context['total_produtos']    = Produto.objects.count()
        seis_meses = hoje - timedelta(days=180)
        vpm = (Venda.objects.filter(status='confirmada', data_venda__gte=seis_meses)
               .annotate(mes=TruncMonth('data_venda')).values('mes')
               .annotate(total_vendas=Count('id')).order_by('mes'))
        context['grafico_meses']   = [v['mes'].strftime('%b/%Y') for v in vpm]
        context['grafico_vendas']  = [v['total_vendas'] for v in vpm]
        ccontext['grafico_receita'] = context['grafico_vendas']
        context['top_produtos'] = (ItemVenda.objects.filter(venda__status='confirmada')
            .values('produto__nome')
            .annotate(total_qtd=Sum('quantidade'), total_valor=Sum('subtotal'))
            .order_by('-total_qtd')[:5])
        return context


class RelatorioVendasView(LoginRequiredMixin, TemplateView):
    template_name = 'relatorios/vendas.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        vendas, data_inicio, data_fim, status = _get_vendas_filtradas(self.request)
        vendas_list = list(vendas)
        context['vendas']      = vendas_list
        context['data_inicio'] = data_inicio or ''
        context['data_fim']    = data_fim or ''
        context['status']      = status or ''
        context['total_geral'] = sum(v.total for v in vendas_list)
        context['total_count'] = len(vendas_list)
        return context
""")
f.close()
print('Parte 1 OK')