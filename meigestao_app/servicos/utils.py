from django.contrib.auth.mixins import LoginRequiredMixin, AccessMixin
from django.shortcuts import redirect
from django.contrib import messages

class CompanyIsolationMixin(AccessMixin):
    """
    Garante que todas as consultas e operações sejam restritas à empresa do usuário logado.
    """
    def get_queryset(self):
        qs = super().get_queryset()
        if hasattr(self.request.user, 'perfil'):
            return qs.filter(empresa=self.request.user.perfil.empresa)
        return qs.none()

    def form_valid(self, form):
        if hasattr(self.request.user, 'perfil'):
            form.instance.empresa = self.request.user.perfil.empresa
            return super().form_valid(form)
        messages.error(self.request, "Usuário sem perfil de empresa associado.")
        return redirect('dashboard')
