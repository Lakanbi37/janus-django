from graphene import relay
from graphene_django import DjangoObjectType

from apps.events.models import Event, Feed, Streams


class EventNode(DjangoObjectType):
    class Meta:
        model = Event
        exclude = ["channel", "key", "pin"]
        interfaces = (relay.Node,)
        filter_fields = {
            "topic": ["icontains", "exact"],
            "code": ["exact"],
            "date": ["exact"],
            "category__name": ["icontains", "exact"]
        }


class FeedNode(DjangoObjectType):
    class Meta:
        model = Feed
        fields = "__all__"
        interfaces = (relay.Node,)
        filter_fields = {
            "channel__name": ["exact", "icontains"]
        }


class StreamsNode(DjangoObjectType):
    class Meta:
        model = Streams
        fields = "__all__"
        interfaces = (relay.Node,)
