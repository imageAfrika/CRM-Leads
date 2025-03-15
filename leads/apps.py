from django.apps import AppConfig


class LeadsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'leads'
    verbose_name = 'Leads'

    def ready(self):
        import leads.signals  # noqa
