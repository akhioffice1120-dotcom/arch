# arch_design/context_processors.py
from .models import SiteConfiguration

def site_config(request):
    """Add site configuration to all templates"""
    try:
        config = SiteConfiguration.objects.first()
        return {
            'site_config': config,
        }
    except:
        return {
            'site_config': None,
        }