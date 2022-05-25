import typing
from pyee.asyncio import AsyncIOEventEmitter
from core.rtc.backend import JanusSocketPlugin, JanusSession
from core.utils import transaction_id


class VideoConference(AsyncIOEventEmitter):

    def __init__(self, username: typing.AnyStr, **kwargs):
        super().__init__(**kwargs)
        self._plugin: typing.Optional[JanusSocketPlugin] = None
        self.username = username

    async def send(self, message):
        return await self._plugin.send(message)

    async def trickle(self, candidates: typing.List[typing.Dict[typing.AnyStr, typing.Any]]):
        return await self._plugin.trickle(candidates)

    async def complete_trickle(self):
        return await self.complete_trickle()

    async def attach(self, session: JanusSession):
        self._plugin = await session.attach("janus.plugin.videoroom")

    async def create(self, room: typing.AnyStr, data: typing.Optional[typing.Dict]):
        message = {"request": "create", "room": room}
        if data:
            message.update(data)
        payload = {
            "body": data
        }
        return await self.send(payload)

    async def moderate(self, room: typing.AnyStr, passcode: typing.AnyStr, data: typing.Dict):
        request = {"request": "moderate", "room": room, "secret": passcode}
        request.update(data)
        payload = {"body": request}
        return await self.send(payload)

    async def kick(self, passcode: str, room: str, uid: str):
        request = dict(request="kick", room=room, secret=passcode, id=uid)
        return await self.send({"body": request})

    async def exists(self, room: typing.AnyStr) -> bool:
        request = dict(request="exists", room=room)
        response = await self.send({"body": request})
        return response["plugindata"]["data"]["exists"]

    async def allowed(self, passcode: typing.AnyStr, room: typing.AnyStr, action: typing.AnyStr,
                      tokens: typing.List[typing.AnyStr]):
        request = dict(request="allowed", room=room, secret=passcode, action=action, allowed=tokens)
        return await self.send({"body": request})

    async def destroy(self, room: typing.AnyStr, passcode: typing.AnyStr):
        request = dict(room=room, secret=passcode, request="destroy")
        return await self.send({"body": request})

    async def edit_room(self, room: typing.AnyStr, passcode: typing.AnyStr, body: typing.Dict):
        request = dict(room=room, secret=passcode, request="edit")
        request.update(body)
        return await self.send({"body": request})

    async def list_publishers(self, room):
        request = dict(request="listparticipants", room=room)
        return await self.send({"body": request})

    @property
    def uid(self):
        return "uid_{}" % transaction_id(16)

    @property
    def pid(self):
        return "vid_{}" % transaction_id()
