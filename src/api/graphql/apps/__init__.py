import graphene
from api.graphql.apps.channels import ChannelMutation, ChannelQuery
from api.graphql.apps.events import EventQuery, EventMutation


class AppQuery(ChannelQuery, EventQuery, graphene.ObjectType):
    """App Level Query"""


class AppMutation(ChannelMutation, EventMutation, graphene.ObjectType):
    """App Level Mutation"""
