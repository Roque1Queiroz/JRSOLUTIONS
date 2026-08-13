from django.contrib import admin
from .models import FichaTecnica, FichaTecnicaItem, OrdemProducao

admin.site.register(FichaTecnica)
admin.site.register(FichaTecnicaItem)
admin.site.register(OrdemProducao)
