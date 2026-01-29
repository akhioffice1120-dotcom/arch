# arch_design/apps.py
from django.apps import AppConfig

class ArchDesignConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'arch_design'
    verbose_name = 'Arch Design & Development'