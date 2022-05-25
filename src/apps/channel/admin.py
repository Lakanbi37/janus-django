from django.contrib import admin
from django.apps import apps
# Register your models here.

channel_app = apps.get_app_config("channel")

for _, model in channel_app.models.items():
    admin.site.register(model)
