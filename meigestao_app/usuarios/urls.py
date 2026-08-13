from django.urls import path
from . import views

app_name = 'usuarios'

urlpatterns = [
    path('', views.UsuarioListView.as_view(), name='usuario_list'),
]
