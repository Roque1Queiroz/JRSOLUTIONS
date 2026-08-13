from django.urls import path
from . import views

app_name = 'servicos'

urlpatterns = [
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('lista/', views.OSListView.as_view(), name='os_list'),
    path('criar/', views.OSCreateView.as_view(), name='os_create'),
    path('<int:pk>/', views.OSDetailView.as_view(), name='os_detail'),
]
