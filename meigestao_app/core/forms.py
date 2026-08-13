from django import forms
from .models import Empresa

class EmpresaSetupForm(forms.ModelForm):
    class Meta:
        model = Empresa
        fields = ['nome', 'cnpj', 'logo']
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Nome Fantasia ou Razão Social'
            }),
            'cnpj': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': '00.000.000/0001-00'
            }),
            'logo': forms.FileInput(attrs={
                'class': 'form-control', 
                'accept': 'image/*'
            }),
        }
