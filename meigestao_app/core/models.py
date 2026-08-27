# -*- coding: utf-8 -*-

from datetime import timedelta

from django.db import models
from django.utils import timezone


class BaseModel(models.Model):
    """Modelo base abstrato para todos os modelos do sistema."""
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')

    class Meta:
        abstract = True


class Empresa(BaseModel):
    """Modelo de Empresa."""
    nome = models.CharField(max_length=255, unique=True, verbose_name='Nome')
    cnpj = models.CharField(max_length=18, unique=True, verbose_name='CNPJ')
    email = models.EmailField(blank=True, null=True, verbose_name='Email')
    telefone = models.CharField(max_length=20, blank=True, null=True, verbose_name='Telefone')
    endereco = models.CharField(max_length=500, blank=True, null=True, verbose_name='Endereço')
    cidade = models.CharField(max_length=100, blank=True, null=True, verbose_name='Cidade')
    estado = models.CharField(max_length=2, blank=True, null=True, verbose_name='Estado')
    cep = models.CharField(max_length=10, blank=True, null=True, verbose_name='CEP')
    ativa = models.BooleanField(default=True, verbose_name='Ativa')
    logo = models.ImageField(upload_to='logos/', blank=True, null=True, verbose_name='Logo da Empresa')
    
    PLANO_CHOICES = [
        ('basico', 'Plano Básico'),
        ('profissional', 'Plano Profissional (PME)'),
        ('enterprise', 'Plano Enterprise (Indústria)'),
    ]
    plano = models.CharField(
        max_length=20, 
        choices=PLANO_CHOICES, 
        default='basico', 
        verbose_name='Plano Contratado',
        help_text='Define as permissões, limites e acessos de módulos da empresa.'
    )
    trial_expira_em = models.DateTimeField(
        null=True, blank=True,
        verbose_name='Término do teste gratuito',
        help_text='Se preenchido, a empresa está em teste grátis com acesso total até esta data.'
    )
    asaas_customer_id = models.CharField(
        max_length=64, blank=True, null=True, verbose_name='ID do cliente no Asaas'
    )
    asaas_subscription_id = models.CharField(
        max_length=64, blank=True, null=True, verbose_name='ID da assinatura no Asaas'
    )

    DIAS_TRIAL = 30

    @property
    def em_teste(self):
        """True enquanto a empresa está dentro da janela de teste grátis (acesso total)."""
        return bool(self.trial_expira_em) and timezone.now() <= self.trial_expira_em

    @property
    def teste_expirado(self):
        """True quando a janela de teste passou e a empresa ainda não converteu para um plano pago."""
        return bool(self.trial_expira_em) and timezone.now() > self.trial_expira_em

    def iniciar_teste(self, dias=None):
        """Inicia (ou reinicia) o teste grátis com acesso total (Enterprise)."""
        self.plano = 'enterprise'
        self.trial_expira_em = timezone.now() + timedelta(days=(dias or self.DIAS_TRIAL))
        self.save(update_fields=['plano', 'trial_expira_em', 'atualizado_em'])

    def converter_plano(self, plano):
        """Converte a empresa para um plano pago, encerrando o teste."""
        self.plano = plano
        self.trial_expira_em = None
        self.save(update_fields=['plano', 'trial_expira_em', 'atualizado_em'])

    class Meta:
        app_label = 'core'
        verbose_name = 'Empresa'
        verbose_name_plural = 'Empresas'
        ordering = ['nome']

    def __str__(self):
        return self.nome

    @property
    def limite_usuarios(self):
        limites = {
            'basico': 2,
            'profissional': 5,
            'enterprise': 20,
        }
        return limites.get(self.plano, 2)

    @property
    def tem_ia(self):
        return self.plano in ['profissional', 'enterprise']

    @property
    def tem_whitelabel(self):
        return self.plano in ['profissional', 'enterprise']

    @property
    def tem_apis_customizadas(self):
        return self.plano == 'enterprise'

    def criar_dados_padrao(self):
        """Cria registros iniciais úteis para uma empresa nova (evita telas com
        listas vazias logo após o cadastro, ex.: categorias de produto)."""
        from meigestao_app.estoque.models import Categoria
        padroes = ['Geral', 'Matéria-prima', 'Acabado', 'Serviço']
        for nome in padroes:
            Categoria.objects.get_or_create(empresa=self, nome=nome)


class Lembrete(BaseModel):
    """Modelo para anotações e lembretes de serviços futuros."""
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='lembretes')
    usuario = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='lembretes')
    titulo = models.CharField(max_length=200, verbose_name="Título")
    conteudo = models.TextField(verbose_name="Conteúdo/Nota")
    data_servico = models.DateField(blank=True, null=True, verbose_name="Data do Serviço")
    CATEGORIA_CHOICES = [
        ('prioridade', '🔴 Prioritário'),
        ('manutencao', '🔵 Manutenção'),
        ('orcamento', '🟢 Orçamento'),
    ]
    categoria = models.CharField(max_length=20, choices=CATEGORIA_CHOICES, default='manutencao', verbose_name="Categoria")
    concluido = models.BooleanField(default=False, verbose_name="Concluído")

    class Meta:
        ordering = ['concluido', '-criado_em']
        verbose_name = 'Lembrete'
        verbose_name_plural = 'Lembretes'

    def __str__(self):
        return self.titulo
