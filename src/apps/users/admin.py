from django.contrib import admin
from django.apps import apps

# Register your models here.

users_app = apps.get_app_config("users")

for _, model in users_app.models.items():
    admin.site.register(model)