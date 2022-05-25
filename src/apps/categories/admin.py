from django.contrib import admin
from django.apps import apps
# Register your models here.

category_app = apps.get_app_config("categories")

for model_name, model in category_app.models.items():
    admin.site.register(model)
