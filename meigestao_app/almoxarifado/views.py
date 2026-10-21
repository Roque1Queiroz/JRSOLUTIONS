from django.db import models
from django.views.generic import ListView, CreateView, DetailView, UpdateView, TemplateView, DeleteView
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from meigestao_app.core.mixins import (
    EmpresaFormMixin,
    EmpresaQuerysetMixin,
    ExigeModuloPermissaoMixin,
    ExigeEscritaModuloMixin,
    ExigeExclusaoModuloMixin,
)
from meigestao_app.core.utils.helpers import get_empresa_do_usuario
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse_lazy
from django.utils import timezone
from django.db.models import Sum
from .models import LocalArmazenamento, Setor, SaldoAlmoxarifado, RequisicaoInterna, ItemRequisicao, EnderecoArmazenamento
from meigestao_app.estoque.models import Produto
from .forms import EnderecoArmazenamentoForm, SetorForm, RequisicaoInternaForm

class AlmoxarifadoDashboardView(LoginRequiredMixin, ExigeModuloPermissaoMixin, TemplateView):
    modulo = 'almoxarifado'
    """
    Dashboard principal do Almoxarifado.
    Visão geral de saldos, alertas e requisições pendentes.
    """
    template_name = 'meigestao_app/almoxarifado/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        empresa = get_empresa_do_usuario(self.request.user)
        # Resumo de Requisições
        requisicoes = RequisicaoInterna.objects.filter(empresa=empresa)
        context['req_pendentes'] = requisicoes.filter(status='SOLICITADO').count()
        context['req_aprovadas'] = requisicoes.filter(status='APROVADO').count()
        
        # Informativos de Estoque
        context['saldos_baixos'] = SaldoAlmoxarifado.objects.filter(
            local__empresa=empresa,
            quantidade__lte=models.F('quantidade_minima')
        ).select_related('produto', 'local')[:5]
        
        # Locais e Setores
        context['locais'] = LocalArmazenamento.objects.filter(empresa=empresa, ativo=True)
        context['setores'] = Setor.objects.filter(empresa=empresa)
        
        return context

class RequisicaoListView(LoginRequiredMixin, ExigeModuloPermissaoMixin, ListView):
    modulo = 'almoxarifado'
    """Lista de requisições internas com filtros"""
    model = RequisicaoInterna
    template_name = 'meigestao_app/almoxarifado/requisicao_list.html'
    context_object_name = 'requisicoes'
    paginate_by = 15

    def get_queryset(self):
        empresa = get_empresa_do_usuario(self.request.user)
        qs = super().get_queryset().filter(empresa=empresa)
        # Se não for gestor ou almoxarife, vê apenas as suas
        permissao = getattr(self.request.user.perfil, 'permissao', None) if hasattr(self.request.user, 'perfil') else None
        if permissao not in ['almoxarife', 'gerente', 'admin'] and not self.request.user.is_superuser:
            qs = qs.filter(solicitante=self.request.user)
        return qs

class RequisicaoCreateView(LoginRequiredMixin, ExigeEscritaModuloMixin, EmpresaFormMixin, CreateView):
    modulo = 'almoxarifado'
    """Criação de nova requisição interna"""
    model = RequisicaoInterna
    template_name = 'meigestao_app/almoxarifado/requisicao_form.html'
    form_class = RequisicaoInternaForm
    success_url = reverse_lazy('almoxarifado:requisicao_list')

    def form_valid(self, form):
        form.instance.solicitante = self.request.user
        # Se o sistema for multi-empresa, pegar a empresa do usuário
        from meigestao_app.core.models import Empresa
        form.instance.empresa = get_empresa_do_usuario(self.request.user)
        
        messages.success(self.request, 'Requisição enviada com sucesso! Aguarde aprovação.')
        return super().form_valid(form)

class RequisicaoDetailView(LoginRequiredMixin, ExigeModuloPermissaoMixin, EmpresaQuerysetMixin, DetailView):
    modulo = 'almoxarifado'
    """Detalhes da requisição e seus itens"""
    model = RequisicaoInterna
    template_name = 'meigestao_app/almoxarifado/requisicao_detail.html'
    context_object_name = 'requisicao'

class RequisicaoAprovarView(LoginRequiredMixin, ExigeEscritaModuloMixin, View):
    modulo = 'almoxarifado'
    """Lógica para aprovação de requisição por gestores"""
    def post(self, request, pk, *args, **kwargs):
        requisicao = get_object_or_404(
            RequisicaoInterna,
            pk=pk,
            empresa=get_empresa_do_usuario(request.user),
        )
        
        permissao = getattr(request.user.perfil, 'permissao', None) if hasattr(request.user, 'perfil') else None
        if permissao not in ['gerente', 'admin'] and not request.user.is_superuser:
            messages.error(request, 'Ação permitida apenas para Gerentes ou Admins.')
            return redirect('almoxarifado:requisicao_detail', pk=pk)

        acao = request.POST.get('acao')
        if acao == 'aprovar':
            requisicao.status = 'APROVADO'
            requisicao.aprovado_por = request.user
            requisicao.data_aprovacao = timezone.now()
            messages.success(request, 'Requisição aprovada com sucesso!')
        elif acao == 'recusar':
            requisicao.status = 'RECUSADO'
            messages.warning(request, 'Requisição recusada.')
        elif acao == 'entregar':
            requisicao.status = 'ENTREGUE'
            # Atualiza quantidades entregues baseado no form se necessário
            # Aqui assume-se que entregou o que foi pedido no MVP
            for item in requisicao.itens.all():
                item.quantidade_entregue = item.quantidade_solicitada
                item.save()
            messages.success(request, 'Materiais entregues e estoque atualizado!')

        requisicao.save()
        return redirect('almoxarifado:requisicao_detail', pk=pk)

# --- NOVAS VIEWS DE ENDEREÇAMENTO E ETIQUETAS ---

class EnderecoListView(LoginRequiredMixin, ExigeModuloPermissaoMixin, ListView):
    modulo = 'almoxarifado'
    """Lista de endereços (Corredores/Prateleiras)"""
    model = EnderecoArmazenamento
    template_name = 'meigestao_app/almoxarifado/endereco_list.html'
    context_object_name = 'enderecos'

    def get_queryset(self):
        empresa = get_empresa_do_usuario(self.request.user)
        return EnderecoArmazenamento.objects.filter(local__empresa=empresa).select_related('local')

class EnderecoCreateView(LoginRequiredMixin, ExigeEscritaModuloMixin, EmpresaFormMixin, CreateView):
    modulo = 'almoxarifado'
    """Cadastro de novo endereço"""
    model = EnderecoArmazenamento
    template_name = 'meigestao_app/almoxarifado/endereco_form.html'
    form_class = EnderecoArmazenamentoForm
    success_url = reverse_lazy('almoxarifado:endereco_list')

    def form_valid(self, form):
        form.instance.empresa = get_empresa_do_usuario(self.request.user)
        messages.success(self.request, 'Endereço cadastrado com sucesso!')
        return super().form_valid(form)

class CentralEtiquetasView(LoginRequiredMixin, ExigeModuloPermissaoMixin, TemplateView):
    modulo = 'almoxarifado'
    """Central para seleção e impressão de etiquetas de locais e produtos"""
    template_name = 'meigestao_app/almoxarifado/central_etiquetas.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        empresa = get_empresa_do_usuario(self.request.user)
        context['locais'] = LocalArmazenamento.objects.filter(empresa=empresa, ativo=True)
        context['enderecos'] = EnderecoArmazenamento.objects.filter(local__empresa=empresa).select_related('local')
        saldos = SaldoAlmoxarifado.objects.filter(local__empresa=empresa).select_related('produto', 'endereco')
        context['produtos'] = saldos
        # Lista de produtos distintos que têm saldo no almoxarifado da empresa.
        # Usada pelo template da etiqueta da peça (precisa acessar produto.sku e produto.id).
        pecas = Produto.objects.filter(
            saldos_almoxarifado__local__empresa=empresa,
        ).distinct().order_by('sku')
        context['pecas'] = pecas
        return context

class PrateleiraView(LoginRequiredMixin, EmpresaQuerysetMixin, DetailView):
    """Visão mobile da prateleira ao escanear QR Code"""
    model = EnderecoArmazenamento
    template_name = 'meigestao_app/almoxarifado/prateleira_view.html'
    context_object_name = 'endereco'
    slug_url_kwarg = 'codigo'
    slug_field = 'codigo_endereco'
    empresa_lookup = 'local__empresa'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        empresa = get_empresa_do_usuario(self.request.user)
        context['materiais'] = SaldoAlmoxarifado.objects.filter(local__empresa=empresa, endereco=self.object)
        return context

class SetorListView(LoginRequiredMixin, ExigeModuloPermissaoMixin, ListView):
    modulo = 'almoxarifado'
    model = Setor
    template_name = 'meigestao_app/almoxarifado/setor_list.html'
    context_object_name = 'setores'

    def get_queryset(self):
        empresa = get_empresa_do_usuario(self.request.user)
        return Setor.objects.filter(empresa=empresa)

class SetorCreateView(LoginRequiredMixin, ExigeEscritaModuloMixin, EmpresaFormMixin, CreateView):
    modulo = 'almoxarifado'
    model = Setor
    form_class = SetorForm
    template_name = 'meigestao_app/almoxarifado/setor_form.html'
    success_url = reverse_lazy('almoxarifado:setor_list')

    def form_valid(self, form):
        form.instance.empresa = get_empresa_do_usuario(self.request.user)
        messages.success(self.request, "Setor cadastrado com sucesso!")
        return super().form_valid(form)

class SetorUpdateView(LoginRequiredMixin, ExigeEscritaModuloMixin, EmpresaQuerysetMixin, EmpresaFormMixin, UpdateView):
    modulo = 'almoxarifado'
    model = Setor
    form_class = SetorForm
    template_name = 'meigestao_app/almoxarifado/setor_form.html'
    success_url = reverse_lazy('almoxarifado:setor_list')

    def form_valid(self, form):
        messages.success(self.request, "Setor atualizado com sucesso!")
        return super().form_valid(form)

class SetorDeleteView(LoginRequiredMixin, ExigeExclusaoModuloMixin, EmpresaQuerysetMixin, DeleteView):
    modulo = 'almoxarifado'
    model = Setor
    template_name = 'meigestao_app/almoxarifado/setor_confirm_delete.html'
    success_url = reverse_lazy('almoxarifado:setor_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Setor excluído com sucesso!")
        return super().delete(request, *args, **kwargs)
