from graphene import relay
from graphene_django import DjangoObjectType

from apps.users.models import User


class UserNode(DjangoObjectType):
    class Meta:
        model = User
        fields = "__all__"
        interfaces = (relay.Node,)
