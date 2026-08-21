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
    # Endpoint JSON seguro que alimenta o assistente de IA com dados da empresa.
    path('bot/contexto/', views.bot_contexto, name='bot_contexto'),
]
