from django.urls import path
from . import views
from . import compromisso_views

app_name = 'financeiro'

urlpatterns = [
    path('', views.TransacaoListView.as_view(), name='transacao_lista'),
    path('criar/', views.TransacaoCreateView.as_view(), name='transacao_criar'),
    path('<int:pk>/', views.TransacaoDetailView.as_view(), name='transacao_detalhe'),
    path('<int:pk>/editar/', views.TransacaoUpdateView.as_view(), name='transacao_editar'),
    path('<int:pk>/deletar/', views.TransacaoDeleteView.as_view(), name='transacao_excluir'),
    path('receitas/', views.ReceitaListView.as_view(), name='receita_lista'),
    path('receitas/criar/', views.ReceitaCreateView.as_view(), name='receita_criar'),
    path('receitas/<int:pk>/', views.ReceitaDetailView.as_view(), name='receita_detalhe'),
    path('receitas/<int:pk>/editar/', views.ReceitaUpdateView.as_view(), name='receita_editar'),
    path('receitas/<int:pk>/deletar/', views.ReceitaDeleteView.as_view(), name='receita_excluir'),
    
    # Reembolsos
    path('reembolsos/', views.ReciboReembolsoListView.as_view(), name='reembolso_lista'),
    path('reembolsos/criar/', views.ReciboReembolsoCreateView.as_view(), name='reembolso_criar'),
    path('reembolsos/<int:pk>/editar/', views.ReciboReembolsoUpdateView.as_view(), name='reembolso_editar'),
    path('reembolsos/<int:pk>/deletar/', views.ReciboReembolsoDeleteView.as_view(), name='reembolso_excluir'),
    path('reembolsos/<int:pk>/pago/', views.ReciboReembolsoToggleView.as_view(), name='reembolso_pago'),

    # Relatórios Financeiros
    path('relatorios/', views.RelatorioFinanceiroListView.as_view(), name='relatorio_list'),
    path('relatorios/criar/', views.RelatorioFinanceiroCreateView.as_view(), name='relatorio_criar'),

    path('parcelas/', compromisso_views.CompromissoListView.as_view(), name='compromisso_lista'),
    path('parcelas/nova/', compromisso_views.CompromissoCreateView.as_view(), name='compromisso_criar'),
    path('parcelas/<int:pk>/', compromisso_views.CompromissoDetailView.as_view(), name='compromisso_detalhe'),
    path('parcelas/<int:pk>/boleto/<int:parcela_id>/', compromisso_views.NossoBoletoView.as_view(), name='nosso_boleto'),
    path('parcelas/<int:pk>/pagar/<int:parcela_id>/', compromisso_views.ParcelaPagarView.as_view(), name='parcela_pagar'),
    path('parcelas/<int:pk>/excluir/', compromisso_views.CompromissoDeleteView.as_view(), name='compromisso_excluir'),
]

