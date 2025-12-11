from django.apps import AppConfig


class CmrConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'cmr'
    def ready(self):
        import pct.signals
