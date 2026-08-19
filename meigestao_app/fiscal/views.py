
from django.shortcuts import get_object_or_404
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView, TemplateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Sum, Count
from django.utils import timezone
from django.http import FileResponse
from datetime import timedelta

from .models import NotaFiscal
from .forms import NotaFiscalForm
from .utils import gerar_pdf_nota_fiscal
from meigestao_app.core.utils.helpers import get_empresa_do_usuario
from meigestao_app.core.mixins import (
    EmpresaQuerysetMixin,
    ExigeModuloPermissaoMixin,
    ExigeEscritaModuloMixin,
    ExigeExclusaoModuloMixin,
)


class NotaFiscalFormEmpresaMixin:
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['empresa'] = get_empresa_do_usuario(self.request.user)
        return kwargs


class NotaFiscalListView(LoginRequiredMixin, ExigeModuloPermissaoMixin, ListView):
    modulo = 'fiscal'
    """Lista todas as Notas Fiscais com filtros avançados"""
    model = NotaFiscal
    template_name = 'meigestao_app/fiscal/nota_fiscal_list.html'
    context_object_name = 'notas_fiscais'
    paginate_by = 10

    def get_create_url(self):
        return reverse_lazy('fiscal:nota_fiscal_create')
    
    def get_queryset(self):
        empresa = get_empresa_do_usuario(self.request.user)
        queryset = NotaFiscal.objects.filter(empresa=empresa).order_by('-data_emissao')
        
        # Filtro por status
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        # Filtro por cliente
        cliente_id = self.request.GET.get('cliente')
        if cliente_id:
            queryset = queryset.filter(cliente_id=cliente_id)
        
        # Filtro por período
        periodo = self.request.GET.get('periodo')
        if periodo == 'hoje':
            queryset = queryset.filter(data_emissao__date=timezone.now().date())
        elif periodo == 'semana':
            data_inicio = timezone.now() - timedelta(days=7)
            queryset = queryset.filter(data_emissao__gte=data_inicio)
        elif periodo == 'mes':
            data_inicio = timezone.now() - timedelta(days=30)
            queryset = queryset.filter(data_emissao__gte=data_inicio)
        
        # Busca por número
        busca = self.request.GET.get('busca')
        if busca:
            queryset = queryset.filter(
                Q(numero__icontains=busca) | 
                Q(cliente__nome__icontains=busca)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        empresa = get_empresa_do_usuario(self.request.user)
        
        # Estatísticas
        context['total_notas'] = NotaFiscal.objects.filter(empresa=empresa).count()
        context['total_valor'] = NotaFiscal.objects.filter(empresa=empresa).aggregate(
            total=Sum('valor_total')
        )['total'] or 0
        context['notas_rascunho'] = NotaFiscal.objects.filter(empresa=empresa, status='rascunho').count()
        context['notas_emitidas'] = NotaFiscal.objects.filter(empresa=empresa, status='emitida').count()
        
        # Filtros aplicados
        context['status_filter'] = self.request.GET.get('status', '')
        context['cliente_filter'] = self.request.GET.get('cliente', '')
        context['periodo_filter'] = self.request.GET.get('periodo', '')
        context['busca_filter'] = self.request.GET.get('busca', '')
        
        return context


class NotaFiscalCreateView(LoginRequiredMixin, ExigeEscritaModuloMixin, NotaFiscalFormEmpresaMixin, CreateView):
    modulo = 'fiscal'
    """Criar nova Nota Fiscal"""
    model = NotaFiscal
    form_class = NotaFiscalForm
    template_name = 'meigestao_app/fiscal/nota_fiscal_form.html'
    success_url = reverse_lazy('fiscal:nota_fiscal_list')
    
    def form_valid(self, form):
        form.instance.empresa = get_empresa_do_usuario(self.request.user)
        form.instance.calcular_total()
        return super().form_valid(form)


class NotaFiscalDetailView(LoginRequiredMixin, ExigeModuloPermissaoMixin, EmpresaQuerysetMixin, DetailView):
    modulo = 'fiscal'
    """Detalhes de uma Nota Fiscal"""
    model = NotaFiscal
    template_name = 'meigestao_app/fiscal/nota_fiscal_detail.html'
    context_object_name = 'nota_fiscal'


class NotaFiscalUpdateView(LoginRequiredMixin, ExigeEscritaModuloMixin, EmpresaQuerysetMixin, NotaFiscalFormEmpresaMixin, UpdateView):
    modulo = 'fiscal'
    """Editar Nota Fiscal"""
    model = NotaFiscal
    form_class = NotaFiscalForm
    template_name = 'meigestao_app/fiscal/nota_fiscal_form.html'
    success_url = reverse_lazy('fiscal:nota_fiscal_list')
    
    def form_valid(self, form):
        form.instance.empresa = get_empresa_do_usuario(self.request.user)
        form.instance.calcular_total()
        return super().form_valid(form)


class NotaFiscalDeleteView(LoginRequiredMixin, ExigeExclusaoModuloMixin, EmpresaQuerysetMixin, DeleteView):
    modulo = 'fiscal'
    """Deletar Nota Fiscal"""
    model = NotaFiscal
    template_name = 'meigestao_app/fiscal/nota_fiscal_confirm_delete.html'
    success_url = reverse_lazy('fiscal:nota_fiscal_list')


class NotaFiscalRelatorioView(LoginRequiredMixin, ExigeModuloPermissaoMixin, TemplateView):
    modulo = 'fiscal'
    """Relatório completo de notas fiscais"""
    template_name = 'meigestao_app/fiscal/nota_fiscal_relatorio.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        empresa = get_empresa_do_usuario(self.request.user)
        
        # Período (padrão: últimos 30 dias)
        data_inicio = self.request.GET.get('data_inicio')
        data_fim = self.request.GET.get('data_fim')
        
        if data_inicio and data_fim:
            notas = NotaFiscal.objects.filter(
                empresa=empresa,
                data_emissao__date__gte=data_inicio,
                data_emissao__date__lte=data_fim
            )
        else:
            data_inicio = timezone.now() - timedelta(days=30)
            notas = NotaFiscal.objects.filter(empresa=empresa, data_emissao__gte=data_inicio)
        
        # Estatísticas gerais
        context['total_notas'] = notas.count()
        context['valor_total'] = notas.aggregate(Sum('valor_total'))['valor_total__sum'] or 0
        context['valor_desconto'] = notas.aggregate(Sum('valor_desconto'))['valor_desconto__sum'] or 0
        context['valor_impostos'] = notas.aggregate(
            total=Sum('valor_icms') + Sum('valor_ipi')
        )['total'] or 0
        
        # Por status (com percentual calculado)
        status_stats = list(notas.values('status').annotate(
            quantidade=Count('id'),
            valor=Sum('valor_total')
        ))
        
        for status in status_stats:
            if context['valor_total'] > 0:
                status['percentual'] = (status['valor'] / context['valor_total']) * 100
            else:
                status['percentual'] = 0
                
        context['por_status'] = status_stats
        
        # Top 10 clientes
        context['top_clientes'] = notas.values('cliente__nome').annotate(
            quantidade=Count('id'),
            valor=Sum('valor_total')
        ).order_by('-valor')[:10]
        
        # Ticket médio
        context['ticket_medio'] = (
            context['valor_total'] / context['total_notas'] 
            if context['total_notas'] > 0 else 0
        )
        
        # Notas recentes
        context['notas_recentes'] = notas.order_by('-data_emissao')[:10]
        
        return context


class NotaFiscalPDFView(LoginRequiredMixin, ExigeModuloPermissaoMixin, EmpresaQuerysetMixin, DetailView):
    modulo = 'fiscal'
    """Gera PDF da nota fiscal"""
    model = NotaFiscal
    
    def get(self, request, *args, **kwargs):
        nota_fiscal = self.get_object()
        pdf_buffer = gerar_pdf_nota_fiscal(nota_fiscal)
        
        return FileResponse(
            pdf_buffer,
            as_attachment=True,
            filename=f"NF_{nota_fiscal.numero}_{nota_fiscal.serie}.pdf"
        )


class NotaFiscalCreateFromVendaView(LoginRequiredMixin, ExigeEscritaModuloMixin, CreateView):
    modulo = 'fiscal'
    """Cria NF a partir de uma venda"""
    model = NotaFiscal
    form_class = NotaFiscalForm
    template_name = 'meigestao_app/fiscal/nota_fiscal_form.html'
    success_url = reverse_lazy('fiscal:nota_fiscal_list')

    def get_venda(self):
        from meigestao_app.vendas.models import Venda

        if not hasattr(self, '_venda'):
            self._venda = get_object_or_404(
                Venda,
                pk=self.kwargs['venda_id'],
                empresa=get_empresa_do_usuario(self.request.user),
            )
        return self._venda
    
    def get_initial(self):
        initial = super().get_initial()
        venda = self.get_venda()
        initial['cliente'] = venda.cliente
        initial['venda'] = venda
        initial['valor_subtotal'] = venda.valor_subtotal
        initial['valor_desconto'] = venda.desconto
        
        return initial
    
    def form_valid(self, form):
        venda = self.get_venda()
        form.instance.empresa = venda.empresa
        form.instance.cliente = venda.cliente
        form.instance.venda = venda
        form.instance.calcular_total()
        return super().form_valid(form)
