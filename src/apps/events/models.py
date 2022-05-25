from channels.db import database_sync_to_async
from django.db import models

# Create your models here.
from apps.security.models import Encryption
from apps.channel.models import Channel
from core.utils import transaction_id


class Event(Encryption):
    """"""
    channel = models.ForeignKey("channel.Channel", on_delete=models.CASCADE, related_name="events")
    presenters = models.ManyToManyField("channel.Channel", related_name="presenters", blank=True)
    code = models.SlugField(null=True, blank=True)
    topic = models.CharField(max_length=120)
    category = models.ForeignKey("categories.Category", on_delete=models.CASCADE, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    date = models.DateTimeField(null=True, blank=True)
    pin = models.CharField(max_length=4, null=True, blank=True)
    feeds = models.ManyToManyField("events.Feed", blank=True)

    created = models.DateTimeField(auto_now_add=True)

    objects = models.Manager()

    def __str__(self):
        return self.topic

    def save(
            self, **kwargs
    ):
        if not self.code:
            self.code = transaction_id(28)
        return super(Event, self).save(**kwargs)

    def streams(self, user):
        streams = list()
        qs = self.feeds.all()
        channel = Channel.get(user=user)
        if channel == self.channel or channel in self.presenters.all():
            qs = self.feeds.exclude(channel=channel)
        for feed in qs:
            streams.extend(feed.to_list)
        return streams

    @database_sync_to_async
    def can_present(self, channel=None):
        if channel is None:
            return False
        return bool(channel == self.channel or channel in self.presenters.all())

    @database_sync_to_async
    def can_subscribe(self, user):
        return bool(not user.is_authenticated or self.presenters.count() > 0)

    @database_sync_to_async
    def add_feed(self, feed, channel, streams):
        new_feed = Feed.objects.create(feed=feed, channel=channel)
        new_streams = [Streams(**stream) for stream in streams]
        stream_list = Streams.objects.bulk_create(new_streams)
        new_feed.streams.add(*stream_list)
        new_feed.save()
        self.feeds.add(new_feed)
        self.feeds.save()


class Feed(models.Model):
    channel = models.ForeignKey("channel.Channel", on_delete=models.CASCADE)
    feed = models.CharField(max_length=220, null=True, blank=True)
    streams = models.ManyToManyField("events.Streams", related_name="streams", blank=True)

    objects = models.Manager()

    def __str__(self):
        return self.feed

    @property
    def to_list(self):
        return list({"feed": self.feed, "mid": mid} for mid in self.streams.all())


class Streams(models.Model):
    """
    "type" : "<type of published stream #1 (audio|video|data)">,
    "mindex" : "<unique mindex of published stream #1>",
    "mid" : "<unique mid of of published stream #1>",
    "disabled" : <if true, it means this stream is currently inactive/disabled (and so codec, description, etc. will be missing)>,
    "codec" : "<codec used for published stream #1>",
    "description" : "<text description of published stream #1, if any>",
    "moderated" : <true if this stream audio has been moderated for this participant>,
    "simulcast" : "<true if published stream #1 uses simulcast (VP8 and H.264 only)>",
    "svc" : "<true if published stream #1 uses SVC (VP9 only)>",
    "talking" : <true|false, whether the publisher stream has audio activity or not (only if audio levels are used)>
    """
    type = models.CharField(max_length=220, null=True, blank=True)
    mindex = models.CharField(max_length=220, null=True, blank=True)
    mid = models.CharField(max_length=220, null=True, blank=True)
    disabled = models.BooleanField(default=False)
    codec = models.CharField(max_length=220, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    moderated = models.BooleanField(default=False)
    simulcast = models.BooleanField(default=False)
    svc = models.BooleanField(default=False)
    talking = models.BooleanField(default=False)

    objects = models.Manager()

    def __str__(self):
        return self.type

    class Meta:
        verbose_name = "streams"
        verbose_name_plural = "streams"
