from django.views.generic import TemplateView, View
from django.db.models import Sum, F, DecimalField, ExpressionWrapper
from django.http import HttpResponse
from django.contrib import messages
from django.shortcuts import redirect
from .utils import render_to_pdf
from django.utils import timezone
from datetime import timedelta
from meigestao_app.vendas.models import Venda, ItemVenda
from meigestao_app.financeiro.models import Transacao, ReciboReembolso
from meigestao_app.estoque.models import Produto
from meigestao_app.core.models import Empresa
from decimal import Decimal
from meigestao_app.almoxarifado.models import RequisicaoInterna, ItemRequisicao, Setor
from meigestao_app.core.utils.helpers import get_empresa_do_usuario




class EmpresaRequeridaMixin:
    """
    Mixin que garante que o usuário possui um Perfil com Empresa vinculada.
    Superusuários e staff passam sem restrição.
    Caso contrário, redireciona para o dashboard com mensagem amigável.
    """
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            empresa = get_empresa_do_usuario(request.user)
            if empresa is None:
                messages.warning(
                    request,
                    '⚠️ Seu usuário não possui uma empresa vinculada. '
                    'Peça ao administrador para configurar seu perfil.'
                )
                return redirect('core:dashboard')
        return super().dispatch(request, *args, **kwargs)

class PainelBIView(EmpresaRequeridaMixin, TemplateView):
    template_name = 'meigestao_app/relatorios/dashboard_bi.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        is_staff = self.request.user.is_staff
        empresa = get_empresa_do_usuario(self.request.user)
        hoje = timezone.now()
        
        # Filtros de Mês e Ano com tratamento de erro robusto
        try:
            mes_atual = int(self.request.GET.get('mes', hoje.month))
            ano_atual = int(self.request.GET.get('ano', hoje.year))
        except (ValueError, TypeError):
            mes_atual = hoje.month
            ano_atual = hoje.year
            
        context['mes_selecionado'] = mes_atual
        context['ano_selecionado'] = ano_atual
        context['anos_disponiveis'] = range(hoje.year - 2, hoje.year + 1)
        context['meses_disponiveis'] = [
            (1, 'Janeiro'), (2, 'Fevereiro'), (3, 'Março'), (4, 'Abril'),
            (5, 'Maio'), (6, 'Junho'), (7, 'Julho'), (8, 'Agosto'),
            (9, 'Setembro'), (10, 'Outubro'), (11, 'Novembro'), (12, 'Dezembro')
        ]

        # --- 1. FATURAMENTO BRUTO ---
        vendas_filter = dict(status__in=['confirmada', 'entregue'],
                             data_venda__month=mes_atual, data_venda__year=ano_atual)
        if not is_staff:
            vendas_filter['empresa'] = empresa
        vendas_query = Venda.objects.filter(**vendas_filter)
        receita_bruta = vendas_query.aggregate(total=Sum('valor_total'))['total'] or Decimal('0.00')

        # --- 2. CMV Otimizado ---
        cmv_agregado = ItemVenda.objects.filter(
            venda__in=vendas_query,
            produto_vinculado__isnull=False
        ).annotate(
            custo_total_item=ExpressionWrapper(
                F('quantidade') * F('produto_vinculado__preco_custo'),
                output_field=DecimalField()
            )
        ).aggregate(total_cmv=Sum('custo_total_item'))['total_cmv'] or Decimal('0.00')

        # --- 3. DESPESAS OPERACIONAIS ---
        desp_filter = dict(tipo='despesa', paga=True,
                           data_transacao__month=mes_atual, data_transacao__year=ano_atual)
        reemb_filter = dict(pago=True,
                            data_compra__month=mes_atual, data_compra__year=ano_atual)
        if not is_staff:
            desp_filter['empresa'] = empresa
            reemb_filter['empresa'] = empresa

        despesas_mes = Transacao.objects.filter(**desp_filter).aggregate(total=Sum('valor'))['total'] or Decimal('0.00')
        reembolsos_mes = ReciboReembolso.objects.filter(**reemb_filter).aggregate(total=Sum('valor'))['total'] or Decimal('0.00')

        despesa_total = despesas_mes + reembolsos_mes

        # --- 4. RESULTADOS FINAIS ---
        lucro_bruto = receita_bruta - cmv_agregado
        lucro_liquido = lucro_bruto - despesa_total
        margem_liquida = (lucro_liquido / receita_bruta * 100) if receita_bruta > 0 else 0

        context['dre'] = {
            'receita_bruta': receita_bruta,
            'cmv': cmv_agregado,
            'lucro_bruto': lucro_bruto,
            'despesas': despesa_total,
            'lucro_liquido': lucro_liquido,
            'margem_liquida': margem_liquida,
        }

        # --- DADOS PARA GRÁFICOS (Últimos 6 Meses) ---
        grafico_labels = []
        grafico_receitas = []
        grafico_despesas = []

        for i in range(5, -1, -1):
            data_alvo = hoje - timedelta(days=i*30)
            mes = data_alvo.month
            ano = data_alvo.year
            
            vf = dict(status__in=['confirmada', 'entregue'],
                      data_venda__month=mes, data_venda__year=ano)
            df = dict(tipo='despesa', paga=True,
                      data_transacao__month=mes, data_transacao__year=ano)
            rf = dict(pago=True, data_compra__month=mes, data_compra__year=ano)
            if not is_staff:
                vf['empresa'] = empresa
                df['empresa'] = empresa
                rf['empresa'] = empresa

            rec  = Venda.objects.filter(**vf).aggregate(total=Sum('valor_total'))['total'] or Decimal('0.00')
            desp = Transacao.objects.filter(**df).aggregate(total=Sum('valor'))['total'] or Decimal('0.00')
            reemb = ReciboReembolso.objects.filter(**rf).aggregate(total=Sum('valor'))['total'] or Decimal('0.00')

            grafico_labels.append(data_alvo.strftime('%b/%y'))
            grafico_receitas.append(float(rec))
            grafico_despesas.append(float(desp + reemb))

        context['grafico_data'] = {
            'labels': grafico_labels,
            'receitas': grafico_receitas,
            'despesas': grafico_despesas,
        }
        return context

class DREExportPDFView(EmpresaRequeridaMixin, View):
    """Gera um PDF formal do DRE baseado nos filtros atuais"""
    def get(self, request):
        empresa = get_empresa_do_usuario(request.user)
        # Tratamento seguro dos parâmetros
        try:
            mes = int(request.GET.get('mes', timezone.now().month))
            ano = int(request.GET.get('ano', timezone.now().year))
        except (ValueError, TypeError):
            mes = timezone.now().month
            ano = timezone.now().year
        
        # Reutilizamos a lógica de cálculo (Poderia ser em um manager para DRY)
        vendas = Venda.objects.filter(empresa=empresa, status__in=['confirmada', 'entregue'], data_venda__month=mes, data_venda__year=ano)
        receita = vendas.aggregate(t=Sum('valor_total'))['t'] or 0
        cmv = ItemVenda.objects.filter(venda__in=vendas, produto_vinculado__isnull=False).annotate(c=F('quantidade')*F('produto_vinculado__preco_custo')).aggregate(t=Sum('c'))['t'] or 0
        desp = Transacao.objects.filter(empresa=empresa, tipo='despesa', paga=True, data_transacao__month=mes, data_transacao__year=ano).aggregate(t=Sum('valor'))['t'] or 0
        reemb = ReciboReembolso.objects.filter(empresa=empresa, pago=True, data_compra__month=mes, data_compra__year=ano).aggregate(t=Sum('valor'))['t'] or 0
        
        data = {
            'empresa': empresa,
            'mes': mes,
            'ano': ano,
            'receita': receita,
            'cmv': cmv,
            'lucro_bruto': receita - cmv,
            'despesa_total': desp + reemb,
            'lucro_liquido': (receita - cmv) - (desp + reemb),
            'data_emissao': timezone.now()
        }
        
        response = render_to_pdf('meigestao_app/relatorios/report_dre_pdf.html', data)
        if response:
            # Força o download do arquivo
            response['Content-Disposition'] = f'attachment; filename="DRE_{mes}_{ano}.pdf"'
            return response
        return HttpResponse("Erro ao gerar PDF", status=400)

class RelatorioConsumoView(EmpresaRequeridaMixin, TemplateView):
    """Relatório de Materiais consumidos por setor (Almoxarifado)"""
    template_name = 'meigestao_app/relatorios/relatorio_consumo.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        empresa = get_empresa_do_usuario(self.request.user)
        
        # Filtro de período simplificado (últimos 30 dias por padrão)
        setores = Setor.objects.filter(empresa=empresa)
        dados_consumo = []
        
        total_geral_valor = Decimal('0.00')

        for setor in setores:
            itens = ItemRequisicao.objects.filter(
                requisicao__setor=setor,
                requisicao__status='ENTREGUE'
            ).annotate(
                valor_consumido=ExpressionWrapper(
                    F('quantidade_entregue') * F('produto__preco_custo'),
                    output_field=DecimalField()
                )
            )
            
            qtd_total = itens.aggregate(t=Sum('quantidade_entregue'))['t'] or 0
            vlr_total = itens.aggregate(t=Sum('valor_consumido'))['t'] or 0
            
            if qtd_total > 0:
                dados_consumo.append({
                    'setor': setor,
                    'quantidade': qtd_total,
                    'valor': vlr_total
                })
                total_geral_valor += vlr_total

        context['dados_consumo'] = sorted(dados_consumo, key=lambda x: x['valor'], reverse=True)
        context['total_geral_valor'] = total_geral_valor
        return context
