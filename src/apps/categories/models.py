from django.db import models
from django.utils.text import slugify

# Create your models here.
from core.utils import image_upload_to


class Category(models.Model):
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True, null=True)
    logo = models.ImageField(upload_to=image_upload_to)
    slug = models.SlugField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def save(
        self, **kwargs
    ):
        if not self.slug:
            self.slug = slugify(self.name)
        return super(Category, self).save(**kwargs)