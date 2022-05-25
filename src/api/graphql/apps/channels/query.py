import graphene
from graphene_django.filter.fields import DjangoFilterConnectionField

from api.graphql.apps.channels.nodes import ChannelNode


class ChannelQuery(graphene.ObjectType):
    channels = DjangoFilterConnectionField(ChannelNode)
    channel = graphene.relay.Node.Field(ChannelNode)
