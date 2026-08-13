from django.utils import timezone
from meigestao_app.core.utils.helpers import get_empresa_do_usuario
from django.views.generic import TemplateView, ListView, CreateView, DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import OrdemServico, ItemOrdemServico
from .utils import CompanyIsolationMixin

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'meigestao_app/servicos/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        empresa = getattr(self.request.user.perfil, 'empresa', None) if hasattr(self.request.user, 'perfil') else None
        
        if empresa:
            qs = OrdemServico.objects.filter(empresa=empresa)
            context['os_abertas'] = qs.filter(status='ABERTA').count()
            context['os_em_execucao'] = qs.filter(status='EXECUCAO').count()
            context['os_finalizadas'] = qs.filter(status='FINALIZADA').count()
            context['ultimas_os'] = qs.order_by('-criado_em')[:5]
            
        return context

class OSListView(LoginRequiredMixin, CompanyIsolationMixin, ListView):
    model = OrdemServico
    template_name = 'meigestao_app/servicos/os_list.html'
    context_object_name = 'ordens'
    paginate_by = 10

class OSCreateView(LoginRequiredMixin, CompanyIsolationMixin, CreateView):
    model = OrdemServico
    template_name = 'meigestao_app/servicos/os_form.html'
    fields = ['tipo', 'cliente', 'responsavel', 'descricao']
    success_url = reverse_lazy('servicos:os_list')

    def form_valid(self, form):
        form.instance.empresa = get_empresa_do_usuario(self.request.user)
        form.instance.solicitante = self.request.user
        messages.success(self.request, "Ordem de Serviço criada com sucesso!")
        return super().form_valid(form)

class OSDetailView(LoginRequiredMixin, CompanyIsolationMixin, DetailView):
    model = OrdemServico
    template_name = 'meigestao_app/servicos/os_detail.html'
    context_object_name = 'os'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from meigestao_app.almoxarifado.models import SaldoAlmoxarifado
        empresa = get_empresa_do_usuario(self.request.user)
        # Lista de materiais da mesma empresa para o modal
        context['materiais_disponiveis'] = SaldoAlmoxarifado.objects.filter(
            local__empresa=empresa
        ).select_related('produto', 'local')
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        
        # Ação 1: Mudar Status
        novo_status = request.POST.get('status')
        if novo_status:
            if novo_status == 'FINALIZADA' and self.object.status != 'FINALIZADA':
                self.processar_baixa_estoque()
            
            self.object.status = novo_status
            if novo_status == 'FINALIZADA':
                self.object.data_fim = timezone.now()
            self.object.save()
            messages.success(request, f"Status da O.S. atualizado para {self.object.get_status_display()}.")

        # Ação 2: Adicionar Material
        material_id = request.POST.get('material_id')
        if material_id:
            from meigestao_app.almoxarifado.models import SaldoAlmoxarifado
            empresa = get_empresa_do_usuario(request.user)
            saldo = get_object_or_404(SaldoAlmoxarifado, pk=material_id, local__empresa=empresa)
            quantidade = int(request.POST.get('quantidade', 1))
            
            ItemOrdemServico.objects.create(
                os=self.object,
                material=saldo,
                quantidade=quantidade,
                preco_unitario=saldo.produto.preco_venda # Seguindo a lógica do sistema
            )
            messages.success(request, f"Material {saldo.produto.nome} adicionado.")

        return redirect('servicos:os_detail', pk=self.object.pk)

    def processar_baixa_estoque(self):
        """Deduz a quantidade dos itens da O.S. do saldo do Almoxarifado."""
        for item in self.object.itens.filter(baixa_estoque=False):
            saldo = item.material
            if saldo.quantidade >= item.quantidade:
                saldo.quantidade -= item.quantidade
                saldo.save()
                item.baixa_estoque = True
                item.save()
            else:
                messages.warning(self.request, f"Estoque insuficiente para {saldo.produto.nome} no local {saldo.local.nome}.")
