import graphene
from apps.channel.models import Channel
from api.graphql.apps.channels.nodes import ChannelNode
from api.graphql.fields.mutation import BaseMutation


class ChannelInput(graphene.InputObjectType):
    id = graphene.String(required=False)
    name = graphene.String(required=True)
    description = graphene.String(required=False)


class ChannelCreate(BaseMutation):
    """"""
    class Meta:
        model = Channel
        lookup_field = "id"

    class Input:
        data = ChannelInput(required=True)

    channel = graphene.Field(ChannelNode)
    ok = graphene.Boolean()

    @classmethod
    def create(cls, request, data):
        if not request.user.is_authenticated:
            return ChannelCreate(ok=False, channel=None)
        channel = Channel.objects.create(user=request.user, name=data["name"], description=data["description"])
        return ChannelCreate(ok=True, channel=channel)

    @classmethod
    def update(cls, instance, request, partial, data):
        if not request.user.is_authenticated:
            return ChannelCreate(ok=False, channel=None)
        instance.name = data.get("name", instance.name)
        instance.description = data.get("description", instance.description)
        instance.save()
        return ChannelCreate(ok=True, channel=instance)


class ChannelMutation(graphene.ObjectType):
    create_channel = ChannelCreate.Field()
