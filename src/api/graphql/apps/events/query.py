import graphene
from graphene import relay
from graphene_django.filter import DjangoFilterConnectionField

from api.graphql.apps.events.node import EventNode


class EventQuery(graphene.ObjectType):
    events = DjangoFilterConnectionField(EventNode)
    event = relay.Node.Field(EventNode)