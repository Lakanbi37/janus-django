import graphene
from django.shortcuts import get_object_or_404
from graphene import InputObjectType
from graphql_relay import from_global_id

from api.graphql.apps.events import EventNode
from api.graphql.fields.mutation import BaseMutation
from apps.categories.models import Category
from apps.channel.models import Channel
from apps.events.models import Event


class EventFields(InputObjectType):
    id = graphene.String(required=False)
    presenters = graphene.List(graphene.String, required=False)
    topic = graphene.String(required=True)
    description = graphene.String(required=False)
    date = graphene.DateTime(required=False)
    pin = graphene.String(required=False)
    password = graphene.String(required=False)
    category = graphene.String(required=False)


class CreateEvent(BaseMutation):
    class Meta:
        model = Event
        lookup_field = "id"

    class Input:
        data = EventFields()

    event = graphene.Field(EventNode)
    ok = graphene.Boolean()

    @classmethod
    def create(cls, request, data):
        if request.user.is_authenticated:
            channel = get_object_or_404(Channel, user=request.user)
            cat_id = data.get("category", None)
            channels = None
            presenters = data.get("presenters")
            if presenters is not None:
                ids = [from_global_id(pid)[1] for pid in presenters]
                channels = Channel.objects.filter(id__in=ids)
            category = None
            if cat_id is not None:
                _, cid = from_global_id(cat_id)
                category = get_object_or_404(Category, id=cid)
            event = Event.objects.create(
                channel=channel,
                topic=data.get("topic"),
                description=data.get("description", None),
                date=data.get("date", None),
                pin=data.get("pin", None),
                category=category
            )
            if channels is not None and len(channels) > 0:
                event.presenters.add(*channels)
            if data.get("password"):
                event.set_encryption_key(raw_key=data["password"])
            event.save()
            return CreateEvent(ok=True, event=event)
        return CreateEvent(ok=False, event=None)

    @classmethod
    def update(cls, instance, request, partial, data):
        if not request.user.is_authenticated:
            return CreateEvent(ok=False, event=None)
        instance.topic = data.get("topic", instance.topic)
        instance.description = data.get("description", instance.description)
        instance.date = data.get("date", instance.date)
        instance.pin = data.get("pin", instance.pin)
        cat_id = data.get("category", None)
        channels = None
        if cat_id is not None:
            _, cid = from_global_id(cat_id)
            category = get_object_or_404(Category, id=cid)
            if category:
                instance.category = category
        presenters = data.get("presenters")
        if presenters is not None:
            ids = [from_global_id(pid)[1] for pid in presenters]
            channels = Channel.objects.filter(id__in=ids)
        if channels is not None and len(channels) > 0:
            instance.presenters.add(*channels)
        if data.get("password"):
            instance.set_encryption_key(raw_key=data["password"])
        instance.save()
        return CreateEvent(ok=True, event=instance)


class EventMutation(graphene.ObjectType):
    create_event = CreateEvent.Field()
