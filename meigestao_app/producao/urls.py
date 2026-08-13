from django.urls import path
from . import views

app_name = 'producao'

urlpatterns = [
    path('', views.PCPDashboardView.as_view(), name='dashboard'),
    
    # Fichas Técnicas
    path('fichas/', views.FichaTecnicaListView.as_view(), name='ficha_tecnica_list'),
    path('fichas/nova/', views.FichaTecnicaCreateView.as_view(), name='ficha_tecnica_create'),
    
    # Ordens de Produção
    path('ordens/', views.OrdemProducaoListView.as_view(), name='ordem_producao_list'),
    path('ordens/nova/', views.OrdemProducaoCreateView.as_view(), name='ordem_producao_create'),
    path('ordens/<int:pk>/', views.OrdemProducaoDetailView.as_view(), name='ordem_producao_detail'),
    path('ordens/<int:pk>/acao/', views.OrdemProducaoActionView.as_view(), name='ordem_producao_action'),
]
