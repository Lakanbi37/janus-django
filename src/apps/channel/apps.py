from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ChannelConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.channel'
    label = "channel"
    verbose_name = "Channel"
