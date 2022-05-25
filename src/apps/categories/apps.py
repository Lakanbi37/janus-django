from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class CategoriesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.categories'
    label = "categories"
    verbose_name = "Category"
    verbose_name_plural = "Categories"
