from django.views.generic import ListView, CreateView, DetailView, UpdateView, TemplateView
from meigestao_app.core.utils.helpers import get_empresa_do_usuario
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin, AccessMixin
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse_lazy
from django.utils import timezone
from django.db import transaction
from .models import FichaTecnica, FichaTecnicaItem, OrdemProducao
from .forms import FichaTecnicaForm, OrdemProducaoForm
from meigestao_app.estoque.models import Produto
from meigestao_app.core.mixins import EmpresaQuerysetMixin


class ProducaoFormEmpresaMixin:
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['empresa'] = get_empresa_do_usuario(self.request.user)
        return kwargs


def get_permissao_usuario(user):
    """Retorna a permissão do perfil do usuário com segurança (evita RelatedObjectDoesNotExist)."""
    try:
        return user.perfil.permissao
    except Exception:
        return None


class PCPAccessMixin(AccessMixin):
    """
    Garante que apenas usuários com nível de Gerente, Admin ou Produção
    possam acessar as funcionalidades do PCP.
    """
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        permissao = get_permissao_usuario(request.user)

        if permissao not in ['producao', 'gerente', 'admin'] and not request.user.is_superuser:
            messages.error(request, "Acesso restrito ao módulo de Produção (PCP).")
            return redirect('core:dashboard')

        return super().dispatch(request, *args, **kwargs)


class PCPDashboardView(LoginRequiredMixin, PCPAccessMixin, TemplateView):
    """Dash principal da fábrica"""
    template_name = 'meigestao_app/producao/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        empresa = get_empresa_do_usuario(self.request.user)
        ops = OrdemProducao.objects.filter(empresa=empresa)

        context['ops_abertas'] = ops.filter(status='ABERTA').count()
        context['ops_em_producao'] = ops.filter(status='PRODUCAO').count()
        context['ops_recentes'] = ops.order_by('-criado_em')[:5]
        context['fichas_count'] = FichaTecnica.objects.filter(empresa=empresa, ativo=True).count()

        return context


# --- GESTÃO DE FICHAS TÉCNICAS (ENGENHARIA) ---

class FichaTecnicaListView(LoginRequiredMixin, PCPAccessMixin, ListView):
    model = FichaTecnica
    template_name = 'meigestao_app/producao/ficha_tecnica_list.html'
    context_object_name = 'fichas'

    def get_queryset(self):
        empresa = get_empresa_do_usuario(self.request.user)
        return FichaTecnica.objects.filter(empresa=empresa)


class FichaTecnicaCreateView(LoginRequiredMixin, PCPAccessMixin, ProducaoFormEmpresaMixin, CreateView):
    model = FichaTecnica
    template_name = 'meigestao_app/producao/ficha_tecnica_form.html'
    form_class = FichaTecnicaForm
    success_url = reverse_lazy('producao:ficha_tecnica_list')

    def form_valid(self, form):
        form.instance.empresa = get_empresa_do_usuario(self.request.user)
        messages.success(self.request, 'Ficha Técnica criada! Agora adicione os componentes.')
        return super().form_valid(form)


# --- GESTÃO DE ORDENS DE PRODUÇÃO (OP) ---

class OrdemProducaoListView(LoginRequiredMixin, PCPAccessMixin, ListView):
    model = OrdemProducao
    template_name = 'meigestao_app/producao/ordem_producao_list.html'
    context_object_name = 'ordens'

    def get_queryset(self):
        empresa = get_empresa_do_usuario(self.request.user)
        return OrdemProducao.objects.filter(empresa=empresa)


class OrdemProducaoCreateView(LoginRequiredMixin, PCPAccessMixin, ProducaoFormEmpresaMixin, CreateView):
    model = OrdemProducao
    template_name = 'meigestao_app/producao/ordem_producao_form.html'
    form_class = OrdemProducaoForm
    success_url = reverse_lazy('producao:ordem_producao_list')

    def form_valid(self, form):
        form.instance.empresa = get_empresa_do_usuario(self.request.user)
        messages.success(self.request, 'Ordem de Produção aberta com sucesso.')
        return super().form_valid(form)


class OrdemProducaoDetailView(LoginRequiredMixin, PCPAccessMixin, EmpresaQuerysetMixin, DetailView):
    model = OrdemProducao
    template_name = 'meigestao_app/producao/ordem_producao_detail.html'
    context_object_name = 'op'


class OrdemProducaoActionView(LoginRequiredMixin, PCPAccessMixin, View):
    """Inicia, Finaliza ou Cancela uma OP"""
    def post(self, request, pk):
        empresa = get_empresa_do_usuario(request.user)
        op = get_object_or_404(OrdemProducao, pk=pk, empresa=empresa)
        acao = request.POST.get('acao')

        try:
            if acao == 'iniciar':
                op.status = 'PRODUCAO'
                op.data_inicio = timezone.now()
                op.save()
                messages.success(request, f'Produção da OP #{op.id} iniciada!')

            elif acao == 'finalizar':
                op.finalizar_producao()
                messages.success(request, f'OP #{op.id} finalizada! Estoque e almoxarifado atualizados.')

            elif acao == 'cancelar':
                op.status = 'CANCELADA'
                op.save()
                messages.warning(request, f'OP #{op.id} cancelada.')

        except Exception as e:
            messages.error(request, f'Erro ao processar OP: {str(e)}')

        return redirect('producao:ordem_producao_detail', pk=pk)
