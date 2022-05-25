from django.contrib import admin
from django.apps import apps

# Register your models here.

stream_apps = apps.get_app_config("events")

for _, model in stream_apps.models.items():
    admin.site.register(model)