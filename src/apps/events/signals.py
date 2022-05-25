from asgiref.sync import async_to_sync
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from channels.layers import get_channel_layer

from apps.events.models import Event, Feed


@receiver(m2m_changed, sender=Event.feeds.through)
def event_feed_changed(sender, instance, action, **kwargs):
    """"""
    if action == "post_add":
        channel_layer = get_channel_layer()
        feeds = list()
        added_feeds = Feed.objects.filter(id__in=kwargs.get("pk_set"))
        for feed in added_feeds:
            if not feed.channel == instance.channel or feed.channel not in instance.presenters.all():
                feeds.extend(feed.to_list)
        if len(feeds) > 0:
            async_to_sync(channel_layer.group_send)(
                instance.code,
                {
                    "type": "send.notification",
                    "event": feeds
                }
            )
