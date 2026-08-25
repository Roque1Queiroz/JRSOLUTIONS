from django import forms
from django.contrib.auth.models import User

from .models import OrdemServico


class OrdemServicoForm(forms.ModelForm):
    """Form de Ordem de Serviço que restringe o responsável a usuários da mesma empresa."""

    class Meta:
        model = OrdemServico
        fields = ["tipo", "cliente", "responsavel", "descricao"]

    def __init__(self, *args, **kwargs):
        empresa = kwargs.pop("empresa", None)
        super().__init__(*args, **kwargs)
        if empresa is not None:
            self.fields["responsavel"].queryset = User.objects.filter(
                perfil__empresa=empresa
            )
        else:
            self.fields["responsavel"].queryset = User.objects.none()
