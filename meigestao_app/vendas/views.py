import logging
from django.db.models import QuerySet, Sum
from django.db import DatabaseError, transaction
from django.http import HttpResponse, HttpRequest
from django.utils.safestring import SafeString
from decimal import Decimal
from typing import Any, Dict, Optional
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils import timezone
from datetime import timedelta
from .models import Venda
from .forms import VendaForm, ItemVendaFormSet
from meigestao_app.core.mixins import EmpresaFormMixin
from meigestao_app.core.utils.helpers import get_empresa_do_usuario

# Configuração de Logs Estruturados (HM-Engineer)
logger = logging.getLogger(__name__)

class VendaListView(LoginRequiredMixin, ListView):
    """Lista todas as vendas com filtragem dinâmica e KPIs."""
    
    model = Venda
    template_name = 'meigestao_app/vendas/venda_list.html'
    context_object_name = 'vendas'
    paginate_by = 20
    login_url = 'admin:login'

    def get_create_url(self):
        return reverse_lazy('vendas:venda_create')

    def get_queryset(self) -> QuerySet:
        """Filtra vendas por empresa e parâmetros de busca."""
        empresa = get_empresa_do_usuario(self.request.user)
        queryset = Venda.objects.filter(empresa=empresa).select_related('cliente', 'transacao_financeira')
        params = self.request.GET
        
        if params.get('status'):
            queryset = queryset.filter(status=params.get('status'))
        if params.get('cliente'):
            queryset = queryset.filter(cliente__nome__icontains=params.get('cliente'))
            
        return queryset.order_by('-data_venda')

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Adiciona dados de contexto e KPIs financeiros."""
        context = super().get_context_data(**kwargs)
        qs = self.get_queryset()

        context['total_vendas_geral'] = qs.count()
        context['valor_total_confirmado'] = qs.filter(
            status='confirmada'
        ).aggregate(total=Sum('valor_total'))['total'] or 0
        context['vendas_pendentes'] = qs.filter(status='rascunho').count()
        context['status_choices'] = Venda.STATUS_CHOICES
        return context


class VendaCreateView(LoginRequiredMixin, EmpresaFormMixin, CreateView):
    """Cria uma nova venda via formulário transacional."""
    
    model = Venda
    form_class = VendaForm
    template_name = 'meigestao_app/vendas/venda_form.html'
    success_url = reverse_lazy('vendas:venda_list')
    login_url = 'admin:login'

    def get_initial(self):
        initial = super().get_initial()
        cliente_id = self.request.GET.get('cliente')
        if cliente_id:
            initial['cliente'] = cliente_id
        return initial

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        form_kwargs = {'empresa': get_empresa_do_usuario(self.request.user)}
        if self.request.POST:
            context['formset'] = ItemVendaFormSet(self.request.POST, form_kwargs=form_kwargs)
        else:
            context['formset'] = ItemVendaFormSet(form_kwargs=form_kwargs)
        return context

    def form_valid(self, form: VendaForm) -> HttpResponse:
        """Salva a venda e seus itens garantindo atomicidade e evitando duplicidade."""
        context = self.get_context_data()
        formset = context['formset']
        
        empresa = get_empresa_do_usuario(self.request.user)
        form.instance.empresa = empresa

        if formset.is_valid():
            # ── TRAVA DE SEGURANÇA: Prevenção de Duplicidade ──
            # Calculamos o subtotal previsto para comparar com vendas recentes
            subtotal_atual = sum(
                (f.cleaned_data.get('quantidade', 0) * f.cleaned_data.get('preco_unitario', 0)
                 for f in formset.forms if f.cleaned_data and not f.cleaned_data.get('DELETE')),
                Decimal('0.00')
            )
            
            # Busca venda idêntica nos últimos 2 minutos
            venda_duplicada = Venda.objects.filter(
                empresa=empresa,
                cliente=form.cleaned_data.get('cliente'),
                valor_subtotal=subtotal_atual,
                criado_em__gte=timezone.now() - timedelta(minutes=2)
            ).exists()

            if venda_duplicada:
                messages.warning(self.request, 'Atenção: Uma venda idêntica para este cliente foi detectada nos últimos 2 minutos. Verifique se não está tentando registrar o mesmo pedido duas vezes.')
                # Se for um POST repetido acidental, bloqueamos. 
                # Se for intencional, o usuário pode esperar um pouco ou mudar algo.
                return self.form_invalid(form)

            try:
                with transaction.atomic():
                    self.object = form.save()
                    formset.instance = self.object
                    formset.save()
                    # Recalcula totais após salvar itens
                    self.object.recalcular_totais()
                    
                logger.info(f"Venda #{self.object.id} criada com sucesso para cliente {self.object.cliente}.")
                messages.success(self.request, 'Venda registrada com sucesso!')
                return redirect('vendas:venda_detail', pk=self.object.pk)
            except (DatabaseError, ValidationError) as e:
                logger.error(f"Falha ao persistir venda no banco: {str(e)}", exc_info=True)
                messages.error(self.request, f'Erro crítico ao salvar a venda: {str(e)}')
                return self.form_invalid(form)
        else:
            return self.form_invalid(form)


class VendaDetailView(LoginRequiredMixin, DetailView):
    """Exibe o detalhamento completo de uma transação específica."""
    
    model = Venda
    template_name = 'meigestao_app/vendas/venda_detail.html'
    context_object_name = 'venda'
    login_url = 'admin:login'

    def get_queryset(self) -> QuerySet:
        empresa = get_empresa_do_usuario(self.request.user)
        return Venda.objects.filter(empresa=empresa).select_related(
            'cliente',
            'transacao_financeira',
            'nota_fiscal',
        )

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['itens'] = self.object.itens.all()
        return context


class VendaUpdateView(LoginRequiredMixin, EmpresaFormMixin, UpdateView):
    """Edita uma venda existente e seus itens relacionados."""
    
    model = Venda
    form_class = VendaForm
    template_name = 'meigestao_app/vendas/venda_form.html'
    success_url = reverse_lazy('vendas:venda_list')
    login_url = 'admin:login'

    def get_queryset(self) -> QuerySet:
        empresa = get_empresa_do_usuario(self.request.user)
        return Venda.objects.filter(empresa=empresa)

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        form_kwargs = {'empresa': get_empresa_do_usuario(self.request.user)}
        if self.request.POST:
            context['formset'] = ItemVendaFormSet(
                self.request.POST,
                instance=self.object,
                form_kwargs=form_kwargs,
            )
        else:
            context['formset'] = ItemVendaFormSet(
                instance=self.object,
                form_kwargs=form_kwargs,
            )
        return context

    def form_valid(self, form: VendaForm) -> HttpResponse:
        """Atualiza a venda garantindo integridade referencial."""
        context = self.get_context_data()
        formset = context['formset']
        
        if formset.is_valid():
            try:
                with transaction.atomic():
                    self.object = form.save()
                    formset.instance = self.object
                    formset.save()
                    # Recalcula totais após salvar itens
                    self.object.recalcular_totais()
                
                logger.info(f"Venda #{self.object.id} atualizada.")
                messages.success(self.request, 'Alterações salvas com sucesso!')
                return redirect('vendas:venda_detail', pk=self.object.pk)
            except (DatabaseError, ValidationError) as e:
                logger.error(f"Erro na atualização da venda #{self.object.id}: {str(e)}", exc_info=True)
                messages.error(self.request, f'Houve um erro técnico na atualização: {str(e)}')
                return self.form_invalid(form)
        else:
            return self.form_invalid(form)


class VendaDeleteView(LoginRequiredMixin, DeleteView):
    """Remove uma venda do sistema."""
    
    model = Venda
    template_name = 'meigestao_app/vendas/venda_confirm_delete.html'
    success_url = reverse_lazy('vendas:venda_list')
    login_url = 'admin:login'

    def get_queryset(self) -> QuerySet:
        empresa = get_empresa_do_usuario(self.request.user)
        return Venda.objects.filter(empresa=empresa)

    def form_valid(self, form: Any) -> HttpResponse:
        venda_id = self.object.id
        try:
            response = super().form_valid(form)
        except (DatabaseError, ValidationError) as exc:
            logger.warning(
                f'Exclusão da venda #{venda_id} recusada: {exc}',
                exc_info=True,
            )
            messages.error(self.request, str(exc))
            return redirect('vendas:venda_detail', pk=venda_id)

        logger.warning(f"Venda #{venda_id} foi excluída permanentemente.")
        messages.success(self.request, 'O registro da venda foi removido.')
        return response
