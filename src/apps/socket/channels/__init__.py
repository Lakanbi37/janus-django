from typing import Optional, Any

from channels.db import database_sync_to_async
from channels.exceptions import AcceptConnection, DenyConnection
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.channel.models import Channel
from apps.stream.models import Stream, Presenter
from core.rtc.apps import MediaSubscribe, MediaPublish
from core.rtc.backend import JanusSocketSession

"""
offer for publishing consists of the SDP offer and payload which contains the codes \n
bit rates and other relative information on the stream to be published
offer format = {"type": "sdpOffer", "msg": {"offer": ..., "payload": ...}}
answer format = {"type: "sdpAnswer", "msg": {"answer": ..., "payload": ...}}
"""


class VideoConferenceConsumer(AsyncJsonWebsocketConsumer):
    class Status(models.IntegerChoices):
        HOST = 1, _('Host')
        CO_HOST = 2, _('Co Host')
        VIEWER = 3, _('Viewer')

    class EventType(models.IntegerChoices):
        OFFER = 1, _("Offer")
        ANSWER = 2, _("Answer")
        ICE = 3, _("Ice")
        ICE_COMPLETE = 4, _("Ice Complete")
        WATCH = 5, _("Watch")
        JOIN_REQUEST = 6, _("Join Request")
        SUBSCRIBE = 7, _("Subscribe")
        UNSUBSCRIBE = 8, _("Unsubscribe")

    def __init__(self, scope):
        super().__init__(scope)
        self._session = JanusSocketSession()
        self._relay: Optional[MediaPublish] = None
        self._subscription: Optional[MediaSubscribe] = None
        self._event_code: Any = None
        self._event = None
        self._user = None
        self._user_status: Optional[int] = None

    async def websocket_connect(self, message):
        self._event_code = self.scope["url_route"]["kwargs"]["code"]
        self._user = self.scope["user"]
        self._event = await self.stream
        await self.set_user_status()
        if self.is_host or self.is_co_host:
            self._relay = MediaPublish(username=self._user.username)
        if self.is_watcher or self.is_co_host:
            self._subscription = MediaSubscribe(username=self._user.username)
        if self.is_host and await self.has_presenters:
            self._subscription = MediaSubscribe(username=self._user.username)
        await self._session.create()
        if self._relay:
            await self._relay.attach(self._session)
        if self._subscription:
            await self._subscription.attach(self._session)
        await self.channel_layer.group_add(self._event_code, self.channel_name)
        try:
            await self.connect()
        except AcceptConnection:
            await self.accept()
        except DenyConnection:
            await self.close()

        await self.create_room()

        await self.send_json(content={"status": self._user_status})

        @self._session.on("event")
        async def on_event(event):
            await self.send_json(content={"event": event})

        if self.is_watcher and self._subscription:
            publishers = await self._subscription.list_publishers(room=self._event_code)
            await self.send_json(content={"publishers": publishers})

    async def receive_json(self, content, **kwargs):
        print(content, {**kwargs})
        event = content["type"]
        if event == self.EventType.OFFER:
            if self._relay:
                offer, payload = content["offer"], content["payload"]
                feed = await self._relay.publish(offer=offer, payload=payload)
                feed_id = feed["plugindata"]["data"]["publishers"][0]["id"]
                streams = feed["plugindata"]["data"]["publishers"][0]["streams"]
                streams["feed"] = feed_id
                if self.is_host:
                    """
                    create streams model object for host channel \n
                    sets the unique publisher's feed
                    """
                    await self._event.add_feed_and_streams(feed_id=feed_id, streams=streams)

                if self.is_co_host:
                    """create streams model object for co hosts \n
                    sets the unique publisher's feed id
                    """
                    presenter = await self.get_channel_presenter
                    await presenter.add_feed_and_streams(feed_id=feed_id, streams=streams)
                    await self.broadcast(msg={"feed": feed_id})
            else:
                await self.send_json(content={"msg": "An error occurred, you cant publish now"})
        if event == self.EventType.JOIN_REQUEST:
            assert self._event.host_feed_id is not None
            assert self._subscription is not None
            _streams = await self._event.host_streams
            offer = await self._subscription.join(room=self._event_code, feed=self._event.host_feed_id, streams=_streams)
            await self.send_json(content={"offer": offer})
        if event == self.EventType.WATCH:
            assert self._subscription is not None
            answer = content["answer"]
            await self._subscription.watch(jsep=answer)
        if event == self.EventType.SUBSCRIBE:
            assert self._subscription is not None
            new_streams = content["streams"]
            offer = await self._subscription.subscribe(streams=new_streams)
            await self.send_json(content={"offer": offer})
        if event == self.EventType.UNSUBSCRIBE:
            assert self._subscription is not None
            streams = content["stream"]
            offer = await self._subscription.unsubscribe(streams=streams)
            await self.send_json(content={"offer": offer})

    async def broadcast(self, msg):
        await self.channel_layer.group_send(self._event_code, {
            "type": "send.message",
            "msg": msg
        })

    async def send_message(self, event):
        await self.send_json(content=event["msg"])

    async def send_notification(self, event):
        await self.send_json(content=event)
        print(f"Got message {event} at {self.channel_name}")

    async def set_user_status(self):
        if self.channel:
            if self.channel == self._event.channel:
                self._user_status = self.Status.HOST
            elif self.channel in self._event.presenters:
                self._user_status = self.Status.CO_HOST
            else:
                await self.close(code=400)
        elif await self.is_viewer:
            self._user_status = self.Status.VIEWER
        else:
            await self.close()

    @property
    @database_sync_to_async
    def stream(self):
        return Stream.objects.get(code=self._event_code)

    @property
    @database_sync_to_async
    def get_channel_presenter(self):
        """gets a Co Presenter channel through model on the Stream() model \n
        this helps us attach the feed id a potential subscriber can subscribe to"""
        return Presenter.objects.get(stream=self._event, presenter=self.channel)

    async def create_room(self):
        publishers = None
        if self._relay:
            room_exists = await self._relay.exists(room=self._event_code)
            if not room_exists:
                room_data = dict()
                if self._event.secret:
                    room_data["secret"] = self._event.key
                if self._event.pin:
                    room_data["pin"] = self._event.pin

                if self.is_host:
                    publishers = await self._relay.create_and_join(room=self._event_code, room_data=room_data)
                elif self.is_co_host:
                    publishers = await self._relay.join(room=self._event_code)
                else:
                    pass
        if publishers:
            await self.broadcast(msg={"publishers": publishers})

    @property
    @database_sync_to_async
    def channel(self):
        try:
            return Channel.get(user=self._user)
        except Channel.DoesNotExist:
            return None

    @property
    @database_sync_to_async
    def has_presenters(self):
        return self.stream.has_presenters

    @property
    @database_sync_to_async
    def is_viewer(self):
        return self.stream.is_viewer(self._user)

    @property
    def is_host(self):
        return bool(self._user_status == self.Status.HOST)

    @property
    def is_co_host(self):
        return self._user_status == self.Status.CO_HOST

    @property
    def is_watcher(self):
        return self._user_status == self.Status.VIEWER

    async def websocket_disconnect(self, message):
        await self.channel_layer.group_discard(self._event_code, self.channel_name)
        await self.close()
