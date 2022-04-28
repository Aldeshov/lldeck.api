from django.apps import AppConfig


class ContentsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'contents'

    def ready(self):
        import contents.signals  # Important!
