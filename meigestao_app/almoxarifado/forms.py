from django import forms
from django.contrib.auth.models import User

from .models import (
    EnderecoArmazenamento,
    LocalArmazenamento,
    RequisicaoInterna,
    Setor,
)


class SetorForm(forms.ModelForm):
    class Meta:
        model = Setor
        fields = ["nome", "descricao", "responsavel"]
        widgets = {
            "nome": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Ex: Manutenção, Administrativo"}
            ),
            "descricao": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "responsavel": forms.Select(attrs={"class": "form-select"}),
        }

    def __init__(self, *args, empresa=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["responsavel"].queryset = (
            User.objects.filter(perfil__empresa=empresa)
            if empresa
            else User.objects.none()
        )


class RequisicaoInternaForm(forms.ModelForm):
    class Meta:
        model = RequisicaoInterna
        fields = ["setor", "local_origem", "justificativa"]
        widgets = {
            "setor": forms.Select(attrs={"class": "form-select"}),
            "local_origem": forms.Select(attrs={"class": "form-select"}),
            "justificativa": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
        }

    def __init__(self, *args, empresa=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["setor"].queryset = (
            Setor.objects.filter(empresa=empresa) if empresa else Setor.objects.none()
        )
        self.fields["local_origem"].queryset = (
            LocalArmazenamento.objects.filter(empresa=empresa, ativo=True)
            if empresa
            else LocalArmazenamento.objects.none()
        )


class EnderecoArmazenamentoForm(forms.ModelForm):
    class Meta:
        model = EnderecoArmazenamento
        fields = ["local", "corredor", "estante", "prateleira", "codigo_endereco"]

    def __init__(self, *args, empresa=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["local"].queryset = (
            LocalArmazenamento.objects.filter(empresa=empresa, ativo=True)
            if empresa
            else LocalArmazenamento.objects.none()
        )
