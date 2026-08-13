# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from meigestao_app.core.models import BaseModel, Empresa

class Perfil(BaseModel):
    """Modelo de Perfil de Usuário."""
    PERMISSOES_CHOICES = [
        ('admin', 'Administrador'),
        ('gerente', 'Gerente'),
        ('vendedor', 'Vendedor'),
        ('operador', 'Operador'),
        ('almoxarife', 'Almoxarife'),
    ]

    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='usuarios')
    permissao = models.CharField(max_length=20, choices=PERMISSOES_CHOICES, default='operador')
    telefone = models.CharField(max_length=20, blank=True, null=True)
    data_admissao = models.DateField()
    ativo = models.BooleanField(default=True)

    class Meta:
        ordering = ['usuario__first_name']
        verbose_name = 'Perfil'
        verbose_name_plural = 'Perfis'

    def __str__(self):
        return f'{self.usuario.get_full_name()} - {self.get_permissao_display()}'

    def clean(self):
        super().clean()
        if not self.pk and self.empresa:
            limite = self.empresa.limite_usuarios
            quantidade_atual = self.empresa.usuarios.count()
            if quantidade_atual >= limite:
                raise ValidationError(
                    f"O limite de usuários para o plano '{self.empresa.get_plano_display()}' "
                    f"da empresa foi atingido (máximo: {limite})."
                )

    def save(self, *args, **kwargs):
        if not self.pk and self.empresa:
            limite = self.empresa.limite_usuarios
            quantidade_atual = self.empresa.usuarios.count()
            if quantidade_atual >= limite:
                raise ValidationError(
                    f"O limite de usuários para o plano '{self.empresa.get_plano_display()}' "
                    f"da empresa foi atingido (máximo: {limite})."
                )
        super().save(*args, **kwargs)
