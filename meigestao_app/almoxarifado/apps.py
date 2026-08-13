from django.apps import AppConfig

class AlmoxarifadoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'meigestao_app.almoxarifado'
    verbose_name = 'Gestão de Almoxarifado'

    def ready(self):
        import meigestao_app.almoxarifado.signals
