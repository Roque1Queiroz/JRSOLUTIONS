# -*- coding: utf-8 -*-
import threading

from django.db import IntegrityError, models, transaction
from django.db.models import Max

from meigestao_app.core.models import BaseModel, Empresa

# Lock em memoria para serializar a atribuicao de codigo de cliente dentro do
# MESMO processo Python (sqlite ignora select_for_update em varias conexoes).
# Cada chave por empresa garante que empresas diferentes nao se bloqueiam.
_codigo_lock_global = threading.Lock()
_codigo_locks_por_empresa = {}


def _lock_por_empresa(empresa_id):
    """Retorna (e cria sob demanda) um lock especifico da empresa."""
    if empresa_id not in _codigo_locks_por_empresa:
        _codigo_locks_por_empresa[empresa_id] = threading.Lock()
    return _codigo_locks_por_empresa[empresa_id]


class Cliente(BaseModel):
    """Modelo de Cliente."""
    TIPO_CHOICES = [
        ('pf', 'Pessoa Física'),
        ('pj', 'Pessoa Jurídica'),
    ]

    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='clientes')
    nome = models.CharField(max_length=255)
    tipo = models.CharField(max_length=2, choices=TIPO_CHOICES, default='pf')
    cpf_cnpj = models.CharField(max_length=18, unique=True)
    email = models.EmailField(blank=True, null=True)
    telefone = models.CharField(max_length=20, blank=True, null=True)
    endereco = models.CharField(max_length=500, blank=True, null=True)
    cidade = models.CharField(max_length=100, blank=True, null=True)
    estado = models.CharField(max_length=2, blank=True, null=True)
    cep = models.CharField(max_length=10, blank=True, null=True)
    ativo = models.BooleanField(default=True)
    codigo = models.PositiveIntegerField(verbose_name='Código')

    class Meta:
        ordering = ['nome']
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        constraints = [
            models.UniqueConstraint(
                fields=['empresa', 'codigo'],
                name='uniq_cliente_empresa_codigo',
            ),
        ]

    def __str__(self):
        return self.nome

    @property
    def codigo_formatado(self):
        from .codigo import formatar_codigo
        return formatar_codigo(self.codigo)

    def save(self, *args, **kwargs):
        if self.codigo or not self.empresa_id:
            return super().save(*args, **kwargs)
        # Serializa por empresa dentro do mesmo processo. Quando o banco
        # for Postgres, select_for_update() dentro do atomic() tambem
        # protege entre processos. No SQLite, este lock em memoria
        # combinado com o UNIQUE constraint e a retry fecha a janela.
        with _codigo_lock_global:
            lock_empresa = _lock_por_empresa(self.empresa_id)
        with lock_empresa:
            ultimo_erro = None
            for _ in range(8):
                try:
                    with transaction.atomic():
                        sequencia, _ = SequenciaCliente.objects.select_for_update().get_or_create(
                            empresa_id=self.empresa_id
                        )
                        # Não usa só o máximo vivo: cliente apagado não devolve o número.
                        maior_vivo = Cliente.objects.filter(empresa_id=self.empresa_id).aggregate(
                            m=Max('codigo')
                        )['m'] or 0
                        proximo = max(sequencia.ultimo, maior_vivo) + 1
                        sequencia.ultimo = proximo
                        sequencia.save(update_fields=['ultimo'])
                        self.codigo = proximo
                        return super().save(*args, **kwargs)
                except IntegrityError as exc:
                    ultimo_erro = exc
                    self.codigo = None
            raise ultimo_erro


class SequenciaCliente(models.Model):
    """Maior código já emitido na empresa. Apagar cliente não devolve o número."""

    empresa = models.OneToOneField(
        Empresa, on_delete=models.CASCADE, related_name='sequencia_cliente'
    )
    ultimo = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = 'Sequência de código do cliente'
        verbose_name_plural = 'Sequências de código do cliente'
