from graphene import relay
from graphene_django import DjangoObjectType

from api.graphql.apps.users.nodes import UserNode # noqa
from apps.channel.models import Channel, Subscriber


class ChannelNode(DjangoObjectType):
    """GraphQl Relay node interface for Channel model"""

    class Meta:
        model = Channel
        interfaces = (relay.Node,)
        fields = "__all__"
        filter_fields = {
            "user__username": ["exact"],
            "user__email": ["exact"],
            "subscribers__username": ["icontains", "exact", "istartswith"],
            "subscribers__email": ["icontains", "exact", "istartswith"]
        }


class SubscribersNode(DjangoObjectType):
    class Meta:
        model = Subscriber
        interfaces = (relay.Node,)
        exclude = ["channel"]
