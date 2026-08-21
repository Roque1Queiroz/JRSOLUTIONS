from django.contrib.auth.mixins import LoginRequiredMixin
from meigestao_app.core.utils.helpers import get_empresa_do_usuario
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView, CreateView, UpdateView, DeleteView, ListView
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.db.models import Count, Sum, Q, F
from django.utils import timezone
from datetime import timedelta
from .models import Empresa
from meigestao_app.clientes.models import Cliente
from meigestao_app.estoque.models import Produto, Estoque
from meigestao_app.vendas.models import Venda, ItemVenda
from meigestao_app.financeiro.models import ContaBancaria, Transacao, ReciboReembolso, RelatorioInteligencia
from meigestao_app.fiscal.models import NotaFiscal
from .models import Empresa, Lembrete
from django.contrib import messages
from django.shortcuts import redirect
from django.core.exceptions import ObjectDoesNotExist
from meigestao_app.financeiro.services import CientistaFinanceiroService
from .forms import EmpresaSetupForm
import json
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseNotFound
from . import asaas

@login_required
def setup_whitelabel(request):
    empresa = _get_user_empresa(request.user)
    if not empresa:
        messages.error(
            request,
            'Não foi possível identificar a empresa vinculada ao seu usuário.',
        )
        return redirect('core:dashboard')

    if request.method == 'POST':
        form = EmpresaSetupForm(request.POST, request.FILES, instance=empresa)
        if form.is_valid():
            nova_empresa = form.save()
            # Garante que o usuário logado está vinculado a esta empresa (se a lógica de Perfil existir)
            if hasattr(request.user, 'perfil'):
                request.user.perfil.empresa = nova_empresa
                request.user.perfil.save()
                
            messages.success(request, 'SISTEMA GESTOR personalizado com sucesso!')
            return redirect('core:dashboard')
    else:
        form = EmpresaSetupForm(instance=empresa)

    return render(request, 'meigestao_app/core/setup_whitelabel.html', {'form': form})


@login_required
def escolher_plano(request):
    """Página apresentada quando o teste grátis (30 dias de acesso total) termina
    e a empresa ainda não converteu: o usuário escolhe um plano para pagar (Asaas).
    """
    empresa = _get_user_empresa(request.user)
    planos = [
        {
            'id': 'basico', 'nome': 'Básico', 'preco': 'R$ 79', 'usuarios': 'até 2 usuários',
            'desc': 'Para começar a organizar o dia a dia.', 'cta': 'Contratar',
            'featured': False,
            'itens': ['Clientes, vendas e estoque', 'Financeiro e fluxo de caixa', 'Assistente de IA incluído'],
        },
        {
            'id': 'profissional', 'nome': 'Profissional', 'preco': 'R$ 199', 'usuarios': 'até 5 usuários',
            'desc': 'O pacote completo para a equipe.', 'cta': 'Contratar',
            'featured': True,
            'itens': ['Tudo do Básico', 'Fiscal, compras, produção e almoxarifado',
                      'Acesso por função (RBAC)', 'Marca personalizada (white label)',
                      'Assistente de IA incluído'],
        },
        {
            'id': 'enterprise', 'nome': 'Enterprise', 'preco': 'R$ 499', 'usuarios': 'até 20 usuários',
            'desc': 'Para operações maiores e integrações customizadas.', 'cta': 'Falar com vendas',
            'featured': False,
            'itens': ['Tudo do Profissional', 'APIs customizadas (integração)',
                      'Marca personalizada (white label)', 'Suporte prioritário',
                      'Assistente de IA incluído'],
        },
    ]
    return render(request, 'meigestao_app/core/escolher_plano.html', {
        'planos': planos,
        'empresa_atual': empresa,
    })


@login_required
def contratar_plano(request):
    """Inicia a assinatura mensal do plano escolhido no Asaas e redireciona para o
    checkout de pagamento. A ativação do plano ocorre no webhook, após confirmação."""
    if request.method != 'POST' or not (plano := request.POST.get('plano', '')):
        return redirect('core:escolher_plano')
    empresa = _get_user_empresa(request.user)
    if not empresa or plano not in asaas.PRECOS:
        messages.error(request, 'Plano inválido.')
        return redirect('core:escolher_plano')
    if not asaas.configurado():
        messages.error(request, 'Pagamento não configurado no momento. Tente mais tarde.')
        return redirect('core:escolher_plano')
    try:
        sub = asaas.criar_assinatura(empresa, plano)
        link = sub and asaas.link_de_pagamento(sub.get('id'))
    except asaas.AsaasError:
        link = None
    if sub and link:
        return redirect(link)
    messages.info(request, 'Cobrança registrada. Finalize o pagamento no Asaas.')
    return redirect('core:escolher_plano')


@csrf_exempt
def asaas_webhook(request):
    """Recebe eventos do Asaas. Em pagamento confirmado/recebido, ativa o plano da
    empresa. Localiza a empresa pelo externalReference (nosso id) ou pelo id da
    assinatura; valida o token do webhook quando configurado."""
    if request.method != 'POST':
        return HttpResponseNotFound()
    try:
        dados = json.loads(request.body or b'{}')
    except ValueError:
        return HttpResponse('bad request', status=400)

    token = getattr(settings, 'ASAAS_WEBHOOK_TOKEN', '')
    if token and dados.get('authToken') != token:
        return HttpResponse('forbidden', status=403)

    evento = str(dados.get('event', '')).upper()
    objeto = (dados.get('subscription') or dados.get('payment')
              or dados.get('object') or dados)
    if not isinstance(objeto, dict):
        return HttpResponse('ok')

    ext = (objeto.get('externalReference') or '').strip()
    sid = objeto.get('id') or ''
    empresa = Empresa.objects.filter(id=int(ext)).first() if ext.isdigit() else None
    if not empresa and sid:
        empresa = Empresa.objects.filter(asaas_subscription_id=sid).first()
    if not empresa:
        return HttpResponse('not found', status=404)

    pagos = {
        'PAYMENT_CONFIRMED', 'PAYMENT_RECEIVED', 'PAYMENT_CREDIT_CARD_CAPTURE_CONFIRMED',
        'SUBSCRIPTION_PAYMENT_CONFIRMED', 'SUBSCRIPTION_PAYMENT_RECEIVED',
    }
    if evento in pagos:
        plano = asaas.plano_por_valor(objeto.get('value'))
        if plano:
            empresa.converter_plano(plano)
    return HttpResponse('ok')

def dashboard(request):
    # Pegamos a empresa do usuário logado
    empresa = _get_user_empresa(request.user)

    # O Cientista faz todo o trabalho duro aqui:
    analise_financeira = CientistaFinanceiroService.gerar_analise_matinal(empresa) if empresa else None

    context = {
        'analise': analise_financeira,
        # ... seus outros dados do dashboard
    }
    return render(request, 'dashboard.html', context)


@login_required
def bot_contexto(request):
    """
    Endpoint APENAS-LEITURA que alimenta o assistente de IA (chatbot) com dados
    reais e agrupados da EMPRESA do usuário logado.

    Segurança:
    - Exige autenticação (@login_required).
    - Usa get_empresa_do_usuario, jamais 'all()': usuários não-staff só enxergam
      a própria empresa. User staff retorna também apenas a empresa vinculada.
    - Não devolve dados sensíveis (CPF/CNPJ completos, senhas, contas detalhadas),
      apenas agregados para o bot responder em linguagem natural.
    """
    from django.http import JsonResponse

    empresa = get_empresa_do_usuario(request.user)
    if not empresa:
        return JsonResponse({"erro": "Empresa não identificada."}, status=403)

    hoje = timezone.now()
    inicio_mes = hoje.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    inicio_hoje = hoje.replace(hour=0, minute=0, second=0, microsecond=0)

    vendas_qs = Venda.objects.filter(empresa=empresa)
    # Faturamento = somatório de vendas CONFIRMADAS (mesma regra do dashboard).
    faturamento_mes = (
        vendas_qs.filter(data_venda__gte=inicio_mes, status='confirmada')
        .aggregate(Sum('valor_total'))['valor_total__sum']
        or 0
    )
    faturamento_hoje = (
        vendas_qs.filter(data_venda__gte=inicio_hoje, status='confirmada')
        .aggregate(Sum('valor_total'))['valor_total__sum']
        or 0
    )
    total_vendas_mes = (
        vendas_qs.filter(data_venda__gte=inicio_mes).exclude(status='cancelada').count()
    )
    vendas_pendentes = (
        vendas_qs.filter(status='rascunho', data_venda__gte=inicio_mes).count()
    )

    return JsonResponse({
        "empresa": empresa.nome,
        "faturamento_mes": float(faturamento_mes),
        "faturamento_hoje": float(faturamento_hoje),
        "total_vendas_mes": total_vendas_mes,
        "vendas_pendentes": vendas_pendentes,
        "nota": "Dados agregados apenas desta empresa, filtrados pelo usuário autenticado.",
    })

def _get_user_empresa(user):
    try:
        return user.perfil.empresa
    except (AttributeError, ObjectDoesNotExist):
        return None

class DashboardView(LoginRequiredMixin, TemplateView):
    """Dashboard principal da aplicação."""
    
    template_name = 'meigestao_app/core/dashboard.html'
    login_url = 'admin:login'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            permissao = getattr(request.user.perfil, 'permissao', None) if hasattr(request.user, 'perfil') else None
            if permissao == 'almoxarife':
                return redirect('almoxarifado:dashboard')
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        hoje = timezone.now()
        inicio_mes = hoje.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        empresa = None if self.request.user.is_staff else _get_user_empresa(self.request.user)

        # Análise do Cientista Financeiro: relatório persistido de hoje ou cálculo ao vivo.
        analise = None
        if empresa is not None:
            data_referencia = timezone.localdate()
            try:
                relatorio = RelatorioInteligencia.objects.get(
                    empresa=empresa, data_referencia=data_referencia
                )
                analise = relatorio.dados_json
            except RelatorioInteligencia.DoesNotExist:
                analise = CientistaFinanceiroService.gerar_analise_matinal(empresa)
        context['analise'] = analise
        context['analise_entradas'] = float((analise or {}).get('entradas_hoje') or 0)
        context['analise_saidas'] = float((analise or {}).get('saidas_hoje') or 0)
        context['analise_projecao'] = float((analise or {}).get('projecao') or 0)

        clientes_qs = Cliente.objects.all() if self.request.user.is_staff else Cliente.objects.filter(empresa=empresa)
        produtos_qs = Produto.objects.all() if self.request.user.is_staff else Produto.objects.filter(empresa=empresa)
        vendas_qs = Venda.objects.all() if self.request.user.is_staff else Venda.objects.filter(empresa=empresa)
        contas_qs = ContaBancaria.objects.all() if self.request.user.is_staff else ContaBancaria.objects.filter(empresa=empresa)
        estoque_qs = Estoque.objects.all() if self.request.user.is_staff else Estoque.objects.filter(produto__empresa=empresa)
        reembolsos_qs = ReciboReembolso.objects.all() if self.request.user.is_staff else ReciboReembolso.objects.filter(empresa=empresa)
        itens_qs = ItemVenda.objects.all() if self.request.user.is_staff else ItemVenda.objects.filter(venda__empresa=empresa)
        lembretes_qs = Lembrete.objects.all() if self.request.user.is_staff else Lembrete.objects.filter(usuario=self.request.user, empresa=empresa)
        
        # Contar registros básicos
        context['total_clientes'] = clientes_qs.count()
        context['total_produtos'] = produtos_qs.count()
        context['total_vendas'] = vendas_qs.count()
        
        # KPIs Financeiros
        context['faturamento_mes'] = vendas_qs.filter(
            data_venda__gte=inicio_mes, 
            status='confirmada'
        ).aggregate(Sum('valor_total'))['valor_total__sum'] or 0
        
        context['saldo_caixa'] = contas_qs.aggregate(Sum('saldo'))['saldo__sum'] or 0
        
        # Alertas de Estoque
        context['estoque_baixo'] = estoque_qs.filter(
            quantidade__lte=F('quantidade_minima')
        ).count()
        
        # Clientes Novos no Mês
        context['clientes_novos'] = clientes_qs.filter(criado_em__gte=inicio_mes).count()
        
        # Dados para o Gráfico Dinâmico
        periodo = self.request.GET.get('periodo', '6m')
        context['current_period'] = periodo
        
        labels_grafico = []
        dados_faturamento = []
        
        if periodo == '7d':
            # Últimos 7 dias
            for i in range(6, -1, -1):
                data_ref = hoje - timedelta(days=i)
                data_ref = data_ref.replace(hour=0, minute=0, second=0, microsecond=0)
                proximo_dia = data_ref + timedelta(days=1)
                
                faturamento = vendas_qs.filter(
                    data_venda__gte=data_ref,
                    data_venda__lt=proximo_dia,
                    status='confirmada'
                ).aggregate(Sum('valor_total'))['valor_total__sum'] or 0
                
                labels_grafico.append(data_ref.strftime('%d/%m'))
                dados_faturamento.append(float(faturamento))
                
        elif periodo == '30d':
            # Últimos 30 dias (agrupado por semana ou dia? vamos por dia para mais detalhe, ou a cada 3 dias)
            for i in range(29, -1, -5): # A cada 5 dias para não poluir
                data_ref = hoje - timedelta(days=i)
                data_ref = data_ref.replace(hour=0, minute=0, second=0, microsecond=0)
                proximo_periodo = data_ref + timedelta(days=5)
                
                faturamento = vendas_qs.filter(
                    data_venda__gte=data_ref,
                    data_venda__lt=proximo_periodo,
                    status='confirmada'
                ).aggregate(Sum('valor_total'))['valor_total__sum'] or 0
                
                labels_grafico.append(data_ref.strftime('%d/%m'))
                dados_faturamento.append(float(faturamento))
        
        else:
            # Padrão meses (6m ou 12m)
            num_meses = 12 if periodo == '12m' else 6
            for i in range(num_meses - 1, -1, -1):
                # Cálculo de meses mais robusto
                ano = hoje.year
                mes = hoje.month - i
                while mes <= 0:
                    mes += 12
                    ano -= 1
                
                mes_ref = hoje.replace(year=ano, month=mes, day=1, hour=0, minute=0, second=0, microsecond=0)
                
                if mes == 12:
                    proximo_mes = mes_ref.replace(year=ano + 1, month=1)
                else:
                    proximo_mes = mes_ref.replace(month=mes + 1)
                
                faturamento = vendas_qs.filter(
                    data_venda__gte=mes_ref,
                    data_venda__lt=proximo_mes,
                    status='confirmada'
                ).aggregate(Sum('valor_total'))['valor_total__sum'] or 0
                
                labels_grafico.append(mes_ref.strftime('%b/%y'))
                dados_faturamento.append(float(faturamento))
            
        context['labels_grafico'] = labels_grafico
        context['dados_faturamento'] = dados_faturamento
        context['has_revenue_data'] = any(valor > 0 for valor in dados_faturamento)
        
        # Ranking de Produtos (Top 5 por quantidade)
        context['produtos_populares'] = itens_qs.values('produto_nome').annotate(
            total_vendido=Sum('quantidade')
        ).order_by('-total_vendido')[:5]
        
        # Vendas Recentes (Sincronizado com o template)
        context['vendas_recentes'] = vendas_qs.select_related('cliente').order_by('-data_venda')[:5]
        context['has_vendas_recentes'] = context['vendas_recentes'].exists()
        
        # Lembretes (Bloco de Notas)
        qs_lembretes = lembretes_qs.filter(concluido=False)
        context['lembretes_ativos'] = qs_lembretes.order_by('-criado_em')[:5]
        context['has_lembretes_ativos'] = context['lembretes_ativos'].exists()
        
        # Reembolsos Pendentes (Para Notificações)
        context['reembolsos_pendentes_count'] = reembolsos_qs.filter(pago=False).count()
        context['reembolsos_pendentes_valor'] = reembolsos_qs.filter(pago=False).aggregate(Sum('valor'))['valor__sum'] or 0
        context['reembolsos_alta_prioridade'] = reembolsos_qs.filter(pago=False, prioridade='alta').count()
        context['has_reembolsos_pendentes'] = context['reembolsos_pendentes_count'] > 0
        
        return context


class LembreteCreateView(LoginRequiredMixin, CreateView):
    """Cria um novo lembrete/nota."""
    model = Lembrete
    fields = ['titulo', 'conteudo', 'data_servico', 'categoria']
    template_name = 'meigestao_app/core/lembrete_form.html'
    success_url = reverse_lazy('core:dashboard')

    def form_valid(self, form):
        form.instance.usuario = self.request.user
        empresa = _get_user_empresa(self.request.user)
        if not empresa:
            form.add_error(None, 'Não foi possível identificar a empresa do usuário.')
            return self.form_invalid(form)
        form.instance.empresa = empresa
        return super().form_valid(form)


class LembreteToggleView(LoginRequiredMixin, UpdateView):
    """Alterna o status de um lembrete (Concluído/Pendente)."""
    model = Lembrete
    fields = []
    success_url = reverse_lazy('core:dashboard')

    def get_queryset(self):
        return super().get_queryset().filter(usuario=self.request.user)

    def post(self, request, *args, **kwargs):
        lembrete = self.get_object()
        lembrete.concluido = not lembrete.concluido
        lembrete.save()
        return redirect(self.success_url)


class LembreteDeleteView(LoginRequiredMixin, DeleteView):
    """Exclui um lembrete."""
    model = Lembrete
    template_name = 'meigestao_app/core/lembrete_confirm_delete.html'
    success_url = reverse_lazy('core:dashboard')

    def get_queryset(self):
        return super().get_queryset().filter(usuario=self.request.user)


class LembreteListView(LoginRequiredMixin, ListView):
    """Página de histórico de todos os lembretes (concluídos e pendentes)."""
    model = Lembrete
    template_name = 'meigestao_app/core/lembrete_list.html'
    context_object_name = 'lembretes'

    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_staff:
            qs = qs.filter(usuario=self.request.user)
        return qs

class HomeView(TemplateView):
    """Página inicial."""
    
    template_name = 'meigestao_app/core/home.html'


@login_required
def plano_detail(request):
    """Página de detalhes e comparação de planos de assinatura."""
    empresa = _get_user_empresa(request.user)
    if not empresa and request.user.is_staff:
        empresa = Empresa.objects.first()

    if not empresa:
        messages.warning(request, "Não foi possível identificar a empresa vinculada ao seu usuário.")
        return redirect('core:dashboard')

    total_usuarios = empresa.usuarios.count()
    limite_usuarios = empresa.limite_usuarios

    # Evita divisão por zero
    if limite_usuarios > 0:
        porcentagem_usuarios = min(int((total_usuarios / limite_usuarios) * 100), 100)
    else:
        porcentagem_usuarios = 0

    context = {
        'empresa': empresa,
        'total_usuarios': total_usuarios,
        'limite_usuarios': limite_usuarios,
        'porcentagem_usuarios': porcentagem_usuarios,
    }
    return render(request, 'meigestao_app/core/plano_detalhes.html', context)
