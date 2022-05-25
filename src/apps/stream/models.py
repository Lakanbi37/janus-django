from django.db import models
from apps.security.models import Encryption

# Create your models here.


class LiveStream(Encryption):
    channel = models.ForeignKey("channel.Channel", on_delete=models.CASCADE, related_name="live_streams")
    name = models.CharField(max_length=120)
    description = models.TextField(null=True, blank=True)
    max_viewers = models.IntegerField(blank=True, null=True)
    code = models.SlugField(null=True, blank=True)
    pin = models.CharField(null=True, blank=True)
    record = models.BooleanField(default=False)
    record_path = models.CharField(max_length=220, null=True, blank=True)
    feeds = models.ManyToManyField("events.Feed", null=True, blank=True, related_name="live_streams")

    objects = models.Manager()

    def __str__(self):
        return self.name
