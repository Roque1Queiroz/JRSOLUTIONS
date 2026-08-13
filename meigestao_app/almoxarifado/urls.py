from django.urls import path
from . import views

app_name = 'almoxarifado'

urlpatterns = [
    path('', views.AlmoxarifadoDashboardView.as_view(), name='dashboard'),
    path('requisicoes/', views.RequisicaoListView.as_view(), name='requisicao_list'),
    path('requisicoes/nova/', views.RequisicaoCreateView.as_view(), name='requisicao_create'),
    path('requisicoes/<int:pk>/', views.RequisicaoDetailView.as_view(), name='requisicao_detail'),
    path('requisicoes/<int:pk>/aprovar/', views.RequisicaoAprovarView.as_view(), name='requisicao_aprovar'),
    
    # Endereçamento e Etiquetas
    path('enderecos/', views.EnderecoListView.as_view(), name='endereco_list'),
    path('enderecos/novo/', views.EnderecoCreateView.as_view(), name='endereco_create'),
    path('etiquetas/', views.CentralEtiquetasView.as_view(), name='central_etiquetas'),
    path('p/<slug:codigo>/', views.PrateleiraView.as_view(), name='prateleira_view'),

    # Setores / Centros de Custo
    path('setores/', views.SetorListView.as_view(), name='setor_list'),
    path('setores/novo/', views.SetorCreateView.as_view(), name='setor_create'),
    path('setores/<int:pk>/editar/', views.SetorUpdateView.as_view(), name='setor_update'),
    path('setores/<int:pk>/excluir/', views.SetorDeleteView.as_view(), name='setor_delete'),
]
