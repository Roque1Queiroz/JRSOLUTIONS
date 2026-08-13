from django import forms
from .models import Setor, RequisicaoInterna, ItemRequisicao

class SetorForm(forms.ModelForm):
    class Meta:
        model = Setor
        fields = ['nome', 'descricao', 'responsavel']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Manutenção, Administrativo'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'responsavel': forms.Select(attrs={'class': 'form-select'}),
        }

class RequisicaoInternaForm(forms.ModelForm):
    class Meta:
        model = RequisicaoInterna
        fields = ['setor', 'local_origem', 'justificativa']
        widgets = {
            'setor': forms.Select(attrs={'class': 'form-select'}),
            'local_origem': forms.Select(attrs={'class': 'form-select'}),
            'justificativa': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
