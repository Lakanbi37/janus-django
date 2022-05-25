from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
# Create your models here.
from core.utils import image_upload_to, AUTH_USER_MODEL


class Channel(models.Model):
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(_("Channel Name"), max_length=120)
    slug = models.SlugField(null=True, blank=True)
    description = models.TextField(_("Channel Description"), null=True, blank=True)
    logo = models.ImageField(_("Logo"), upload_to=image_upload_to)
    background = models.ImageField(_("Background"), upload_to=image_upload_to)
    created = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated = models.DateTimeField(auto_now=True, null=True, blank=True)
    subscribers = models.ManyToManyField(AUTH_USER_MODEL, related_name="subscriptions",
                                         through="Subscriber", through_fields=("channel", "user"))

    objects = models.Manager()

    def __str__(self):
        return self.name

    def save(
        self, **kwargs
    ):
        if not self.slug:
            self.slug = slugify(self.name)
        return super(Channel, self).save(**kwargs)

    @property
    def channel_logo(self):
        return self.logo.url

    @staticmethod
    def get(*args, **kwargs):
        return Channel.objects.get(*args, **kwargs)


class Subscriber(models.Model):
    channel = models.ForeignKey("channel.Channel", on_delete=models.CASCADE, related_name="subscriber")
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="subscription")
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.channel

