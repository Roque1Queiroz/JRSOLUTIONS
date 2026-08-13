from django.contrib.auth.mixins import LoginRequiredMixin
from meigestao_app.core.utils.helpers import get_empresa_do_usuario
from django.views.generic import ListView
from .models import Perfil


class UsuarioListView(LoginRequiredMixin, ListView):
    model = Perfil
    template_name = 'meigestao_app/usuarios/usuario_list.html'
    context_object_name = 'usuarios'
    login_url = 'admin:login'
