# -*- coding: utf-8 -*-
"""Gerencia os dados de demonstração do painel /demo/.

Uso:
    python manage.py seed_demo            # cria/reusa os dados demo (idempotente)
    python manage.py seed_demo --reset    # apaga a empresa demo e recria
"""
from django.core.management.base import BaseCommand

from meigestao_app.core.demo_data import DEMO_CNPJ, seed_demo_db
from meigestao_app.core.models import Empresa


class Command(BaseCommand):
    help = "Gera os dados de demonstração (empresa fictícia) do painel /demo/."

    def add_arguments(self, parser):
        parser.add_argument("--reset", action="store_true", help="Apaga a empresa demo e recria.")

    def handle(self, *args, **options):
        if options["reset"]:
            Empresa.objects.filter(cnpj=DEMO_CNPJ).delete()
            self.stdout.write("Empresa demo removida para reset.")
        empresa = seed_demo_db()
        self.stdout.write(self.style.SUCCESS(
            f"Dados de demonstração prontos — empresa '{empresa.nome}' (id {empresa.pk})."
        ))
