from typing import Optional, AnyStr

from channels.db import database_sync_to_async
from channels.exceptions import AcceptConnection, DenyConnection
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.db import models
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _

from apps.channel.models import Channel
from apps.events.models import Event
from apps.users.models import User
from core.rtc.apps import MediaSubscribe, MediaPublish
from core.rtc.backend import JanusSocketSession


class EventStreamConsumer(AsyncJsonWebsocketConsumer):

    class EventType(models.IntegerChoices):
        PUBLISH = 1, _("Publish")
        ANSWER = 2, _("Answer")
        ICE = 3, _("Ice")
        ICE_COMPLETE = 4, _("Ice Complete")
        TRICKLE = 9, _("Trickle")
        COMPLETE_TRICKLE = 6, _("Complete Trickle")
        WATCH = 5, _("Watch")
        SUBSCRIBE = 7, _("Subscribe")
        UNSUBSCRIBE = 8, _("Unsubscribe")

    def __init__(self, scope):
        super().__init__(scope)
        self._event: Optional[Event] = None
        self._code: Optional[AnyStr] = None
        self._session = JanusSocketSession()
        self._relay: Optional[MediaPublish] = None
        self._receiver: Optional[MediaSubscribe] = None
        self._user: Optional[User] = None
        self._channel: Optional[Channel] = None
        self._receiving = False

    async def websocket_connect(self, message):
        self._code = self.scope["url_route"]["kwargs"]["code"]
        self._user = self.scope["user"]
        self._event = await self.event()
        self._channel = await self.channel()
        await self.channel_layer.group_add(self._code, self.channel_name)
        try:
            await self.connect()
        except AcceptConnection:
            await self.accept()
        except DenyConnection:
            await self.close()

        await self._session.create()
        can_present = await self._event.can_present(channel=self._channel)
        can_subscribe = await self._event.can_subscribe(user=self._user)
        if can_present:
            self._relay = MediaPublish(username=self._user.username)
            await self._relay.attach(self._session)
        if can_subscribe:
            self._receiver = MediaSubscribe(username='')
            await self._receiver.attach(self._session)

        @self._session.on("event")
        async def on_event(event):
            await self.send_json(content={"event": event})

        @self._receiver.on("offer")
        async def on_offer(offer):
            await self.send_json(content={"offer": offer})

        @self._receiver.on("event")
        async def on_event(event):
            await self.send_json(content={"receiver_event": event})

        @self._relay.on("answer")
        async def on_answer(answer):
            await self.send_json(content={"answer": answer})

        await self.create_room()

    async def receive_json(self, content, **kwargs):
        print(content, kwargs)
        event = content["type"]
        if event == self.EventType.PUBLISH.value:
            """"""
            offer, payload = content["offer"], content["payload"]
            feed, answer = await self._relay.publish(offer=offer, payload=payload)
            await self._event.add_feed(feed=feed["id"], streams=feed["streams"], channel=self._channel)
            await self.send_json(content={"answer": answer})
        if event == self.EventType.SUBSCRIBE.value:
            if not self._receiving:
                offer = self._receiver.join(room=self._code,
                                            streams=content["msg"]["streams"],
                                            props=content["msg"]["props"])
                await self.send_json(content={"offer": offer})
            else:
                offer = await self._receiver.subscribe(streams=content["msg"]["streams"])
                await self.send_json(content={"offer": offer})
        if event == self.EventType.ICE.value:
            await self._receiver.trickle(candidates=content["msg"]["candidates"])
        if event == self.EventType.ICE_COMPLETE.value:
            await self._receiver.complete_trickle()
        if event == self.EventType.TRICKLE.value:
            await self._relay.trickle(candidates=content["msg"]["candidates"])
        if event == self.EventType.COMPLETE_TRICKLE.value:
            await self._relay.complete_trickle()
        if event == self.EventType.WATCH.value:
            await self._receiver.watch(jsep=content["msg"]["answer"])
        if event == self.EventType.UNSUBSCRIBE.value:
            offer = await self._receiver.unsubscribe(streams=content["msg"]["streams"])
            await self.send_json(content={"offer": offer})

    @database_sync_to_async
    def event(self):
        return get_object_or_404(Event, code=self._code)

    @database_sync_to_async
    def channel(self):
        try:
            return Channel.get(user=self._user)
        except Channel.DoesNotExists:
            return None

    async def create_room(self):
        if self._channel == self._event.channel:
            room_exists = await self._relay.exists(self._code)
            if not room_exists:
                room_data = dict()
                if self._event.model_is_encrypted:
                    room_data["secret"] = self._event.key
                if self._event.pin:
                    room_data["pin"] = self._event.pin
                await self._relay.create(room=self._code, data=room_data)
        pass

    async def broadcast(self, msg):
        await self.channel_layer.group_send(self._code, {
            "type": "send.message",
            "msg": msg
        })

    async def send_message(self, event):
        await self.send_json(content=event["msg"])

    async def send_notification(self, event):
        await self.send_json(content=event)
        print(f"Got message {event} at {self.channel_name}")
