import logging
from datetime import date
from types import SimpleNamespace
from django.db import transaction
from django.db.models import QuerySet, Sum, Q
from django import forms
from django.http import HttpResponse, HttpRequest
from typing import Any, Dict, Optional
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView, FormView, TemplateView
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.shortcuts import redirect
from .models import Transacao, ReciboReembolso, ContaBancaria
from .forms import TransacaoForm, ReciboReembolsoForm
from meigestao_app.usuarios.models import Perfil
from meigestao_app.core.utils.helpers import get_empresa_do_usuario
from meigestao_app.core.models import Empresa

# Configuração de Logs (HM-Engineer)
logger = logging.getLogger(__name__)


# HM-Engineer: Removido helper local duplicado em favor do meigestao_app.core.utils.helpers.get_empresa_do_usuario


def _get_user_perfil(user: Any) -> Optional[Perfil]:
    try:
        return user.perfil
    except (AttributeError, ObjectDoesNotExist):
        return None


def _aplicar_efeito_saldo(transacao: Transacao, reverse: bool = False) -> None:
    if not transacao.conta or not transacao.paga:
        return

    # Recarrega a conta do banco para evitar aplicar o saldo sobre um objeto stale
    # durante fluxos de update/delete dentro da mesma requisição.
    transacao.conta.refresh_from_db(fields=['saldo'])
    valor = transacao.valor
    if transacao.tipo == 'despesa':
        delta = valor
        transacao.conta.saldo += delta if reverse else -delta
    elif transacao.tipo == 'receita':
        delta = valor
        transacao.conta.saldo += -delta if reverse else delta

    transacao.conta.save(update_fields=['saldo'])


def _transacao_vinculada_reembolso(transacao: Transacao) -> bool:
    try:
        _ = transacao.reembolso_origem
        return True
    except ReciboReembolso.DoesNotExist:
        return False


class RelatorioFinanceiroForm(forms.Form):
    PERIODO_CHOICES = [
        ('mensal', 'Mensal'),
        ('trimestral', 'Trimestral'),
        ('anual', 'Anual'),
        ('personalizado', 'Personalizado'),
    ]

    empresa = forms.ModelChoiceField(queryset=Empresa.objects.none(), label='Empresa')
    titulo = forms.CharField(max_length=120, label='Título')
    periodo = forms.ChoiceField(choices=PERIODO_CHOICES, label='Período')
    data_inicio = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), label='Data Início')
    data_fim = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), label='Data Fim')

    def __init__(self, *args: Any, user: Optional[Any] = None, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        empresa = get_empresa_do_usuario(user) if user else None

        if user and user.is_staff:
            self.fields['empresa'].queryset = Empresa.objects.all().order_by('nome')
        else:
            self.fields['empresa'].queryset = Empresa.objects.filter(pk=empresa.pk) if empresa else Empresa.objects.none()
            if empresa:
                self.fields['empresa'].initial = empresa

        if not self.initial.get('titulo'):
            self.initial['titulo'] = 'Relatório Financeiro'
        if not self.initial.get('periodo'):
            self.initial['periodo'] = 'mensal'
        if not self.initial.get('data_inicio'):
            self.initial['data_inicio'] = date.today().replace(day=1)
        if not self.initial.get('data_fim'):
            self.initial['data_fim'] = date.today()

        for field_name, field in self.fields.items():
            css_class = 'form-select' if isinstance(field.widget, forms.Select) else 'form-control'
            field.widget.attrs['class'] = css_class

    def clean(self) -> Dict[str, Any]:
        cleaned = super().clean()
        data_inicio = cleaned.get('data_inicio')
        data_fim = cleaned.get('data_fim')
        if data_inicio and data_fim and data_inicio > data_fim:
            self.add_error('data_fim', 'A data final deve ser igual ou posterior à data inicial.')
        return cleaned


class RelatorioFinanceiroCreateView(LoginRequiredMixin, FormView):
    template_name = 'meigestao_app/financeiro/relatorio_form.html'
    form_class = RelatorioFinanceiroForm
    success_url = reverse_lazy('financeiro:relatorio_list')

    def get_form_kwargs(self) -> Dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form: RelatorioFinanceiroForm) -> HttpResponse:
        empresa = form.cleaned_data['empresa']
        params = (
            f"?empresa={empresa.pk}"
            f"&titulo={form.cleaned_data['titulo']}"
            f"&periodo={form.cleaned_data['periodo']}"
            f"&data_inicio={form.cleaned_data['data_inicio'].isoformat()}"
            f"&data_fim={form.cleaned_data['data_fim'].isoformat()}"
        )
        return redirect(f"{self.success_url}{params}")


class RelatorioFinanceiroListView(LoginRequiredMixin, TemplateView):
    template_name = 'meigestao_app/financeiro/relatorio_list.html'

    def _build_relatorio(self, empresa: Empresa, titulo: str, periodo: str, data_inicio: date, data_fim: date) -> Any:
        qs = Transacao.objects.filter(empresa=empresa, data_transacao__gte=data_inicio, data_transacao__lte=data_fim)
        total_receitas = qs.filter(tipo='receita').aggregate(total=Sum('valor'))['total'] or 0
        total_despesas = qs.filter(tipo='despesa').aggregate(total=Sum('valor'))['total'] or 0
        saldo_liquido = total_receitas - total_despesas
        periodo_display = dict(RelatorioFinanceiroForm.PERIODO_CHOICES).get(periodo, 'Personalizado')
        querystring = (
            f"empresa={empresa.pk}"
            f"&titulo={titulo}"
            f"&periodo={periodo}"
            f"&data_inicio={data_inicio.isoformat()}"
            f"&data_fim={data_fim.isoformat()}"
        )
        return SimpleNamespace(
            pk=1,
            titulo=titulo,
            periodo=periodo,
            periodo_display=periodo_display,
            data_inicio=data_inicio,
            data_fim=data_fim,
            total_receitas=total_receitas,
            total_despesas=total_despesas,
            saldo_liquido=saldo_liquido,
            querystring=querystring,
        )

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['relatorios'] = []

        empresa_id = self.request.GET.get('empresa')
        titulo = self.request.GET.get('titulo')
        periodo = self.request.GET.get('periodo')
        data_inicio_raw = self.request.GET.get('data_inicio')
        data_fim_raw = self.request.GET.get('data_fim')

        if not all([empresa_id, titulo, periodo, data_inicio_raw, data_fim_raw]):
            return context

        try:
            empresa = Empresa.objects.get(pk=empresa_id)
            if not self.request.user.is_staff:
                user_empresa = get_empresa_do_usuario(self.request.user)
                if not user_empresa or user_empresa.pk != empresa.pk:
                    return context

            data_inicio = date.fromisoformat(data_inicio_raw)
            data_fim = date.fromisoformat(data_fim_raw)
            if data_inicio > data_fim:
                return context

            relatorio = self._build_relatorio(empresa, titulo, periodo, data_inicio, data_fim)
            context['relatorios'] = [relatorio]
        except (Empresa.DoesNotExist, ValueError):
            context['relatorios'] = []

        return context


class FluxoTransacaoMixin:
    tipo_fixo: Optional[str] = None
    flow_singular = 'Transação'
    flow_plural = 'Transações'
    list_page_title = 'Fluxo de Caixa'
    list_heading = 'Histórico de Transações'
    list_subtitle = 'Visão detalhada das movimentações financeiras recentes.'
    form_subtitle = 'Gerenciamento de entrada e saída do fluxo de caixa.'
    detail_page_title = 'Detalhes da Transação'
    delete_page_title = 'Excluir Transação'
    create_button_label = 'Nova Transação'
    empty_title = 'Nenhuma movimentação'
    empty_description = 'Suas transações registradas aparecerão aqui.'
    paid_status_label = 'Liquidada'
    paid_help_text = 'Marque se o valor já foi pago ou recebido.'
    icon_class = 'bi bi-cash-stack'
    list_url_name = 'financeiro:transacao_lista'
    create_url_name = 'financeiro:transacao_criar'
    detail_url_name = 'financeiro:transacao_detalhe'
    update_url_name = 'financeiro:transacao_editar'
    delete_url_name = 'financeiro:transacao_excluir'

    def get_queryset(self) -> QuerySet:
        qs = super().get_queryset()
        if self.request.user.is_staff:
            user_qs = qs
        else:
            empresa = get_empresa_do_usuario(self.request.user)
            user_qs = qs.filter(empresa=empresa) if empresa else qs.none()

        if self.tipo_fixo:
            user_qs = user_qs.filter(tipo=self.tipo_fixo)

        return user_qs

    def get_success_url(self) -> str:
        return reverse(self.list_url_name)

    def _build_kpi_cards(self, qs: QuerySet) -> list[dict[str, Any]]:
        total_receitas = qs.filter(tipo='receita').aggregate(total=Sum('valor'))['total'] or 0
        total_despesas = qs.filter(tipo='despesa').aggregate(total=Sum('valor'))['total'] or 0

        if self.tipo_fixo == 'receita':
            receitas_recebidas = qs.filter(paga=True).aggregate(total=Sum('valor'))['total'] or 0
            receitas_pendentes = qs.filter(paga=False).aggregate(total=Sum('valor'))['total'] or 0
            return [
                {
                    'title': 'Receitas',
                    'value': total_receitas,
                    'border_color': '#10b981',
                    'icon_wrapper_class': 'bg-success bg-opacity-10 text-success',
                    'icon_class': 'bi bi-graph-up-arrow',
                    'value_class': 'text-success',
                },
                {
                    'title': 'Recebidas',
                    'value': receitas_recebidas,
                    'border_color': '#0ea5e9',
                    'icon_wrapper_class': 'bg-info bg-opacity-10 text-info',
                    'icon_class': 'bi bi-check-circle',
                    'value_class': 'text-info',
                },
                {
                    'title': 'Pendentes',
                    'value': receitas_pendentes,
                    'border_color': '#f59e0b',
                    'icon_wrapper_class': 'bg-warning bg-opacity-10 text-warning',
                    'icon_class': 'bi bi-clock-history',
                    'value_class': 'text-warning',
                },
            ]

        return [
            {
                'title': 'Receitas',
                'value': total_receitas,
                'border_color': '#10b981',
                'icon_wrapper_class': 'bg-success bg-opacity-10 text-success',
                'icon_class': 'bi bi-graph-up-arrow',
                'value_class': 'text-success',
            },
            {
                'title': 'Despesas',
                'value': total_despesas,
                'border_color': '#ef4444',
                'icon_wrapper_class': 'bg-danger bg-opacity-10 text-danger',
                'icon_class': 'bi bi-graph-down-arrow',
                'value_class': 'text-danger',
            },
            {
                'title': 'Saldo Líquido',
                'value': total_receitas - total_despesas,
                'border_color': '#4f46e5',
                'icon_wrapper_class': 'bg-primary bg-opacity-10 text-primary',
                'icon_class': 'bi bi-wallet2',
                'value_class': 'text-primary',
            },
        ]

    def _flow_context(self) -> Dict[str, Any]:
        singular = self.flow_singular
        editando = bool(getattr(getattr(self, 'object', None), 'pk', None))
        return {
            'flow_page_title': self.list_page_title,
            'flow_heading': self.list_heading,
            'flow_subtitle': self.list_subtitle,
            'flow_form_title': f"Editar {singular}" if editando else f"Nova {singular}",
            'flow_form_subtitle': self.form_subtitle,
            'flow_detail_page_title': self.detail_page_title,
            'flow_delete_page_title': self.delete_page_title,
            'flow_delete_heading': 'Confirmar Exclusão',
            'flow_singular': singular,
            'flow_plural': self.flow_plural,
            'flow_create_button_label': self.create_button_label,
            'flow_save_button_label': f"SALVAR {singular.upper()}",
            'flow_empty_title': self.empty_title,
            'flow_empty_description': self.empty_description,
            'flow_paid_status_label': self.paid_status_label,
            'flow_pending_status_label': 'Pendente',
            'flow_paid_help_text': self.paid_help_text,
            'flow_icon_class': self.icon_class,
            'flow_show_tipo_field': self.tipo_fixo is None,
            'flow_list_url': reverse(self.list_url_name),
            'flow_create_url': reverse(self.create_url_name),
            'flow_detail_url_name': self.detail_url_name,
            'flow_edit_url_name': self.update_url_name,
            'flow_delete_url_name': self.delete_url_name,
        }

    def _prepare_form_for_flow(self, form: TransacaoForm) -> TransacaoForm:
        if self.tipo_fixo and 'tipo' in form.fields:
            form.fields['tipo'].initial = self.tipo_fixo
            form.fields['tipo'].widget = forms.HiddenInput()
        return form

    def _apply_tipo_fixo(self, transacao: Transacao) -> None:
        if self.tipo_fixo:
            transacao.tipo = self.tipo_fixo


class TransacaoListView(FluxoTransacaoMixin, LoginRequiredMixin, ListView):
    """Lista de transações financeiras com KPIs."""
    model = Transacao
    template_name = 'meigestao_app/financeiro/transacao_list.html'
    context_object_name = 'transacoes'
    login_url = 'admin:login'

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        qs = self.get_queryset()

        receitas = qs.filter(tipo='receita').aggregate(total=Sum('valor'))['total'] or 0
        despesas = qs.filter(tipo='despesa').aggregate(total=Sum('valor'))['total'] or 0

        context['total_receitas'] = receitas
        context['total_despesas'] = despesas
        context['saldo_liquido'] = receitas - despesas
        context['kpi_cards'] = self._build_kpi_cards(qs)
        context.update(self._flow_context())
        return context


class TransacaoDetailView(FluxoTransacaoMixin, LoginRequiredMixin, DetailView):
    model = Transacao
    template_name = 'meigestao_app/financeiro/transacao_detail.html'
    context_object_name = 'transacao'

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context.update(self._flow_context())
        return context


class TransacaoCreateView(FluxoTransacaoMixin, LoginRequiredMixin, CreateView):
    model = Transacao
    form_class = TransacaoForm
    template_name = 'meigestao_app/financeiro/transacao_form.html'

    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if request.user.is_authenticated and not request.user.is_staff:
            empresa = get_empresa_do_usuario(request.user)
            perfil_ativo = getattr(getattr(request.user, 'perfil', None), 'ativo', False)
            if not empresa or not perfil_ativo:
                raise PermissionDenied('Usuário sem vínculo empresarial ativo.')
        return super().dispatch(request, *args, **kwargs)

    def get_form(self, form_class: Optional[type] = None) -> Any:
        form = super().get_form(form_class)
        empresa = get_empresa_do_usuario(self.request.user)
        
        if empresa and 'empresa' in form.fields:
            if not self.request.user.is_staff:
                form.fields['empresa'].queryset = form.fields['empresa'].queryset.filter(pk=empresa.pk)
            form.fields['empresa'].initial = empresa
            
        if 'conta' in form.fields:
            if not self.request.user.is_staff:
                form.fields['conta'].queryset = ContaBancaria.objects.filter(empresa=empresa, ativa=True) if empresa else ContaBancaria.objects.none()
            elif empresa:
                # Para staff, tenta pré-filtrar contas da empresa selecionada inicialmente
                form.fields['conta'].queryset = ContaBancaria.objects.filter(empresa=empresa, ativa=True)

        return self._prepare_form_for_flow(form)

    def form_valid(self, form: TransacaoForm) -> HttpResponse:
        self._apply_tipo_fixo(form.instance)
        
        # Para usuários comuns, a empresa é sempre definida pelo vínculo do perfil.
        # Nunca confiar no ID de empresa enviado pelo navegador.
        if not self.request.user.is_staff:
            empresa = get_empresa_do_usuario(self.request.user)
            if not empresa:
                raise PermissionDenied('Usuário sem vínculo empresarial ativo.')
            form.instance.empresa = empresa
        elif not form.instance.empresa_id:
            empresa = get_empresa_do_usuario(self.request.user)
            if not empresa:
                messages.error(self.request, 'Não foi possível identificar a empresa para esta transação.')
                return self.form_invalid(form)
            form.instance.empresa = empresa

        if form.instance.conta and form.instance.conta.empresa_id != form.instance.empresa_id:
            form.add_error('conta', 'A conta selecionada não pertence à empresa informada.')
            return self.form_invalid(form)

        if (
            form.instance.paga
            and form.instance.tipo == 'despesa'
            and form.instance.conta
            and form.instance.conta.saldo < form.instance.valor
        ):
            form.add_error('valor', 'Saldo insuficiente na conta selecionada para lançar esta despesa como liquidada.')
            return self.form_invalid(form)

        with transaction.atomic():
            response = super().form_valid(form)
            _aplicar_efeito_saldo(self.object)

        messages.success(self.request, f'{self.flow_singular} registrada com sucesso!')
        return response

    def form_invalid(self, form: TransacaoForm) -> HttpResponse:
        logger.warning(f"Tentativa de salvar transação inválida: {form.errors}")
        return super().form_invalid(form)

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context.update(self._flow_context())
        return context


class TransacaoUpdateView(FluxoTransacaoMixin, LoginRequiredMixin, UpdateView):
    model = Transacao
    form_class = TransacaoForm
    template_name = 'meigestao_app/financeiro/transacao_form.html'

    def get_form(self, form_class: Optional[type] = None) -> Any:
        form = super().get_form(form_class)
        empresa = self.object.empresa
        if 'conta' in form.fields:
            form.fields['conta'].queryset = ContaBancaria.objects.filter(empresa=empresa, ativa=True)
        if not self.request.user.is_staff and 'empresa' in form.fields:
            form.fields['empresa'].queryset = form.fields['empresa'].queryset.filter(pk=empresa.pk)
            form.fields['empresa'].initial = empresa
        return self._prepare_form_for_flow(form)

    def form_valid(self, form: TransacaoForm) -> HttpResponse:
        if _transacao_vinculada_reembolso(self.object):
            messages.error(self.request, 'Transações geradas por reembolso não podem ser editadas. Faça o estorno no reembolso.')
            return redirect(self.detail_url_name, pk=self.object.pk)

        if not self.request.user.is_staff:
            form.instance.empresa = self.object.empresa

        self._apply_tipo_fixo(form.instance)

        if form.instance.conta and form.instance.conta.empresa_id != form.instance.empresa_id:
            form.add_error('conta', 'A conta selecionada não pertence à empresa informada.')
            return self.form_invalid(form)

        transacao_anterior = Transacao.objects.select_related('conta').get(pk=self.object.pk)
        with transaction.atomic():
            _aplicar_efeito_saldo(transacao_anterior, reverse=True)

            if (
                form.instance.paga
                and form.instance.tipo == 'despesa'
                and form.instance.conta
                and form.instance.conta.saldo < form.instance.valor
            ):
                form.add_error('valor', 'Saldo insuficiente na conta selecionada para liquidar esta despesa.')
                transaction.set_rollback(True)
                return self.form_invalid(form)

            response = super().form_valid(form)
            _aplicar_efeito_saldo(self.object, reverse=False)

        messages.success(self.request, f'{self.flow_singular} atualizada com sucesso!')
        return response

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context.update(self._flow_context())
        return context


class TransacaoDeleteView(FluxoTransacaoMixin, LoginRequiredMixin, DeleteView):
    model = Transacao
    template_name = 'meigestao_app/financeiro/transacao_confirm_delete.html'
    context_object_name = 'transacao'

    def delete(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        self.object = self.get_object()
        if _transacao_vinculada_reembolso(self.object):
            messages.error(request, 'Transações geradas por reembolso não podem ser excluídas por aqui. Use o estorno do reembolso.')
            return redirect(self.detail_url_name, pk=self.object.pk)

        with transaction.atomic():
            _aplicar_efeito_saldo(self.object, reverse=True)
            response = super().delete(request, *args, **kwargs)

        messages.success(request, f'{self.flow_singular} excluída com sucesso!')
        return response

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context.update(self._flow_context())
        return context


class ReceitaFlowMixin(FluxoTransacaoMixin):
    tipo_fixo = 'receita'
    flow_singular = 'Receita'
    flow_plural = 'Receitas'
    list_page_title = 'Receitas'
    list_heading = 'Histórico de Receitas'
    list_subtitle = 'Acompanhe entradas previstas, recebidas e a origem das receitas.'
    form_subtitle = 'Cadastre e acompanhe entradas financeiras sem sair do módulo financeiro.'
    detail_page_title = 'Detalhes da Receita'
    delete_page_title = 'Excluir Receita'
    create_button_label = 'Nova Receita'
    empty_title = 'Nenhuma receita cadastrada'
    empty_description = 'As receitas registradas para a empresa aparecerão aqui.'
    paid_status_label = 'Recebida'
    paid_help_text = 'Marque se o valor já foi recebido.'
    icon_class = 'bi bi-graph-up-arrow'
    list_url_name = 'financeiro:receita_lista'
    create_url_name = 'financeiro:receita_criar'
    detail_url_name = 'financeiro:receita_detalhe'
    update_url_name = 'financeiro:receita_editar'
    delete_url_name = 'financeiro:receita_excluir'


class ReceitaListView(ReceitaFlowMixin, TransacaoListView):
    pass


class ReceitaDetailView(ReceitaFlowMixin, TransacaoDetailView):
    pass


class ReceitaCreateView(ReceitaFlowMixin, TransacaoCreateView):
    pass


class ReceitaUpdateView(ReceitaFlowMixin, TransacaoUpdateView):
    pass


class ReceitaDeleteView(ReceitaFlowMixin, TransacaoDeleteView):
    pass


class ReciboReembolsoListView(LoginRequiredMixin, ListView):
    """Lista os recibos de funcionários para reembolso com filtros e segurança."""
    model = ReciboReembolso
    template_name = 'meigestao_app/financeiro/reembolso_list.html'
    context_object_name = 'reembolsos'

    def get_queryset(self) -> QuerySet:
        qs = super().get_queryset()
        if not self.request.user.is_staff:
            qs = qs.filter(colaborador__usuario=self.request.user)
        
        q = self.request.GET.get('q')
        if q:
            qs = qs.filter(
                Q(item__icontains=q) | 
                Q(colaborador__usuario__username__icontains=q) | 
                Q(colaborador__usuario__first_name__icontains=q) |
                Q(nome_solicitante__icontains=q)
            )
            
        status = self.request.GET.get('status')
        if status == 'pago':
            qs = qs.filter(pago=True)
        elif status == 'pendente':
            qs = qs.filter(pago=False)
            
        return qs

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        
        qs_base = super().get_queryset()
        if not self.request.user.is_staff:
            qs_base = qs_base.filter(colaborador__usuario=self.request.user)
            
        total_pago = qs_base.filter(pago=True).aggregate(total=Sum('valor'))['total'] or 0
        total_pendente = qs_base.filter(pago=False).aggregate(total=Sum('valor'))['total'] or 0
        total_geral = total_pago + total_pendente

        context['total_pendente'] = total_pendente
        
        # Adiciona os cards coloridos para a página de reembolsos
        context['kpi_cards'] = [
            {
                'title': 'Total em Recibos',
                'value': total_geral,
                'border_color': '#6366f1',
                'icon_wrapper_class': 'bg-primary bg-opacity-10 text-primary',
                'icon_class': 'bi bi-receipt',
                'value_class': 'text-primary',
            },
            {
                'title': 'Já Reembolsado',
                'value': total_pago,
                'border_color': '#10b981',
                'icon_wrapper_class': 'bg-success bg-opacity-10 text-success',
                'icon_class': 'bi bi-check-all',
                'value_class': 'text-success',
            },
            {
                'title': 'Aguardando',
                'value': total_pendente,
                'border_color': '#f59e0b',
                'icon_wrapper_class': 'bg-warning bg-opacity-10 text-warning',
                'icon_class': 'bi bi-hourglass-split',
                'value_class': 'text-warning',
            },
        ]

        empresa = get_empresa_do_usuario(self.request.user)
        context['contas_bancarias'] = (
            ContaBancaria.objects.filter(empresa=empresa, ativa=True)
            if empresa
            else ContaBancaria.objects.none()
        )

        return context


class ReciboReembolsoCreateView(LoginRequiredMixin, CreateView):
    """Cadastro de novo recibo para reembolso."""
    model = ReciboReembolso
    form_class = ReciboReembolsoForm
    template_name = 'meigestao_app/financeiro/reembolso_form.html'
    success_url = reverse_lazy('financeiro:reembolso_lista')

    def get_form_kwargs(self) -> Dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        kwargs['empresa'] = get_empresa_do_usuario(self.request.user)
        return kwargs

    def get_form(self, form_class: Optional[type] = None) -> Any:
        # HM-Engineer: O formulário já cuida da filtragem no __init__
        return super().get_form(form_class)

    def form_valid(self, form: Any) -> HttpResponse:
        empresa = get_empresa_do_usuario(self.request.user)
        
        # Se for staff e selecionou um colaborador, usamos a empresa do colaborador
        if self.request.user.is_staff and form.instance.colaborador:
            empresa = form.instance.colaborador.empresa
        
        if not empresa:
            messages.error(self.request, 'Não foi possível identificar a empresa para este reembolso.')
            return self.form_invalid(form)

        form.instance.empresa = empresa

        # Validação extra se o colaborador for informado
        if form.instance.colaborador and form.instance.colaborador.empresa_id != form.instance.empresa_id:
            form.add_error('colaborador', 'Colaborador não pertence à empresa selecionada.')
            return self.form_invalid(form)

        messages.success(self.request, 'Recibo enviado com sucesso!')
        return super().form_valid(form)


class ReciboReembolsoObjetoMixin:
    """Restringe objetos de reembolso ao usuário comum autenticado."""

    def get_queryset(self) -> QuerySet:
        qs = super().get_queryset()
        if self.request.user.is_staff:
            return qs
        return qs.filter(
            empresa=get_empresa_do_usuario(self.request.user),
            colaborador__usuario=self.request.user,
        )


class ReciboReembolsoUpdateView(
    LoginRequiredMixin,
    ReciboReembolsoObjetoMixin,
    UpdateView,
):
    """Edição de recibo de reembolso."""
    model = ReciboReembolso
    form_class = ReciboReembolsoForm
    template_name = 'meigestao_app/financeiro/reembolso_form.html'
    success_url = reverse_lazy('financeiro:reembolso_lista')

    def get_form_kwargs(self) -> Dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        kwargs['empresa'] = self.object.empresa
        return kwargs

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        obj = self.get_object()
        if obj.pago and not request.user.is_staff:
            messages.error(request, 'Este reembolso já foi pago e não pode mais ser editado.')
            return redirect('financeiro:reembolso_lista')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form: Any) -> HttpResponse:
        messages.success(self.request, 'Solicitação atualizada com sucesso!')
        return super().form_valid(form)


class ReciboReembolsoDeleteView(
    LoginRequiredMixin,
    ReciboReembolsoObjetoMixin,
    DeleteView,
):
    """Exclusão de recibo de reembolso."""
    model = ReciboReembolso
    template_name = 'meigestao_app/financeiro/reembolso_confirm_delete.html'
    success_url = reverse_lazy('financeiro:reembolso_lista')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        obj = self.get_object()
        if obj.pago:
            messages.error(request, 'Não é possível excluir um reembolso que já foi pago. Estorne o pagamento primeiro.')
            return redirect('financeiro:reembolso_lista')
        return super().dispatch(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Solicitação excluída com sucesso!')
        return super().delete(request, *args, **kwargs)


class ReciboReembolsoToggleView(LoginRequiredMixin, UpdateView):
    """Alterna o status de pagamento e gera transação financeira manual/automática."""
    model = ReciboReembolso
    fields = []
    success_url = reverse_lazy('financeiro:reembolso_lista')

    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if not request.user.is_staff:
            raise PermissionDenied("Somente administradores podem alterar o status de pagamento.")

        reembolso = self.get_object()
        
        # HM-Engineer: Lógica transacional resiliente (transaction.atomic)
        with transaction.atomic():
            reembolso.pago = not reembolso.pago
            
            if reembolso.pago:
                # Escolha de conta enviada pelo modal
                conta_id = request.POST.get('conta_id')
                empresa = reembolso.empresa
                conta = None
                if conta_id:
                    conta = ContaBancaria.objects.filter(
                        pk=conta_id,
                        empresa=empresa,
                        ativa=True
                    ).first()
                    if not conta:
                        messages.error(request, 'Conta bancária inválida para este reembolso.')
                        return redirect(self.success_url)
                else:
                    # Fallback (se não enviado ou automação antiga)
                    conta = ContaBancaria.objects.filter(empresa=empresa, ativa=True).first()

                if conta and conta.saldo < reembolso.valor:
                    messages.error(request, f'Saldo insuficiente na conta {conta.banco} para pagar este reembolso.')
                    return redirect(self.success_url)
                
                if reembolso.colaborador:
                    nome_colaborador = reembolso.colaborador.usuario.get_full_name() or reembolso.colaborador.usuario.username
                else:
                    nome_colaborador = reembolso.nome_solicitante or "Solicitante Externo"
                
                transacao = Transacao.objects.create(
                    empresa=reembolso.empresa,
                    conta=conta,
                    tipo='despesa',
                    categoria='Reembolso de Colaborador',
                    descricao=f"Reembolso: {reembolso.item} ({nome_colaborador})",
                    valor=reembolso.valor,
                    data_transacao=timezone.now().date(),
                    paga=True
                )
                reembolso.transacao = transacao
                
                if conta:
                    conta.saldo -= reembolso.valor
                    conta.save()
                    logger.info(f"Reembolso #{reembolso.id} pago via conta {conta.banco}. Saldo atual: {conta.saldo}")
                    
                messages.success(request, f'Reembolso de R$ {reembolso.valor} pago via {conta.banco if conta else "Caixa"}!')
            else:
                # Logica de Estorno
                if reembolso.transacao:
                    transacao = reembolso.transacao
                    if transacao.conta:
                        transacao.conta.saldo += transacao.valor
                        transacao.conta.save()
                    
                    transacao_id = transacao.id
                    transacao.delete()
                    reembolso.transacao = None
                    logger.warning(f"Pagamento do reembolso #{reembolso.id} estornado. Transação TR-{transacao_id} removida.")
                    
                messages.warning(request, 'Pagamento cancelado e saída removida do Fluxo de Caixa.')

            reembolso.save()
            
        return redirect(self.success_url)
