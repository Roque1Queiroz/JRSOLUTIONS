from django.urls import path
from . import views

app_name = 'core'  # CRÍTICO: Define o namespace

urlpatterns = [
    # Dashboard
    path('', views.DashboardView.as_view(), name='dashboard'),
    
    # Empresas
    path('empresas/', views.EmpresaListView.as_view(), name='empresa_list'),
    path('empresas/criar/', views.EmpresaCreateView.as_view(), name='empresa_create'),
    path('empresas/<int:pk>/', views.EmpresaDetailView.as_view(), name='empresa_detail'),
    path('empresas/<int:pk>/editar/', views.EmpresaUpdateView.as_view(), name='empresa_update'),
    path('empresas/<int:pk>/deletar/', views.EmpresaDeleteView.as_view(), name='empresa_delete'),
]