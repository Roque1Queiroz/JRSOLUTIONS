from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('setup-empresa/', views.setup_whitelabel, name='setup_whitelabel'),
    path('lembretes/', views.LembreteListView.as_view(), name='lembrete_lista'),
    path('lembrete/criar/', views.LembreteCreateView.as_view(), name='lembrete_criar'),
    path('lembrete/<int:pk>/toggle/', views.LembreteToggleView.as_view(), name='lembrete_concluir'),
    path('lembrete/<int:pk>/excluir/', views.LembreteDeleteView.as_view(), name='lembrete_excluir'),
    path('plano/', views.plano_detail, name='plano_detail'),
    path('escolher-plano/', views.escolher_plano, name='escolher_plano'),
    path('contratar-plano/', views.contratar_plano, name='contratar_plano'),
    path('asaas/webhook/', views.asaas_webhook, name='asaas_webhook'),
    # Cadastro self-service (landing): cria Empresa + usuário admin + 30 dias de trial.
    path('cadastro/', views.cadastro, name='cadastro'),
    # Login/logout público do cliente (substitui a tela do Django admin na rotina normal).
    path('entrar/', views.login_view, name='login'),
    path('sair/', views.logout_view, name='logout'),
    # Endpoint JSON seguro que alimenta o assistente de IA com dados da empresa.
    path('bot/contexto/', views.bot_contexto, name='bot_contexto'),
]
