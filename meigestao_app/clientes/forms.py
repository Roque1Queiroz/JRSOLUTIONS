from django import forms
from django.core.exceptions import ValidationError
from .models import Cliente

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = [ 'nome', 'tipo', 'cpf_cnpj', 'email', 'telefone', 'endereco', 'cidade', 'estado', 'cep', 'ativo']
        widgets = {
            'empresa': forms.Select(attrs={'class': 'form-control'}),
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo': forms.Select(attrs={'class': 'form-control'}),
            'cpf_cnpj': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control'}),
            'endereco': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'cidade': forms.TextInput(attrs={'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
            'cep': forms.TextInput(attrs={'class': 'form-control'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean_cpf_cnpj(self):
        cpf_cnpj = self.cleaned_data.get('cpf_cnpj')
        if not cpf_cnpj:
            raise ValidationError('Este campo é obrigatório.')

        import re
        apenas_numeros = re.sub(r'[^0-9]', '', str(cpf_cnpj))

        from validate_docbr import CPF, CNPJ

        if len(apenas_numeros) == 11:
            if not CPF().validate(apenas_numeros):
                raise ValidationError('CPF inválido. Verifique os números e tente novamente.')
        elif len(apenas_numeros) == 14:
            if not CNPJ().validate(apenas_numeros):
                raise ValidationError('CNPJ inválido. Verifique os números e tente novamente.')
        else:
            raise ValidationError('Documento incompleto/inválido. O CPF deve ter 11 dígitos e o CNPJ 14 dígitos.')

        if Cliente.objects.filter(cpf_cnpj=cpf_cnpj).exclude(pk=self.instance.pk).exists():
            raise ValidationError('Este CPF/CNPJ já está cadastrado em outro cliente.')

        return cpf_cnpj

    def clean_cep(self):
        cep = self.cleaned_data.get('cep')
        if cep:
            import re
            apenas_numeros = re.sub(r'[^0-9]', '', str(cep))
            if len(apenas_numeros) != 8:
                raise ValidationError('CEP incompleto. O CEP deve conter exatamente 8 números.')
        return cep

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and Cliente.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise ValidationError('Este e-mail já está cadastrado para outro cliente.')
        return email