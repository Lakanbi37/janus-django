from typing import Optional, Dict, AnyStr, Any

from core.rtc.apps.conference import VideoConference


class MediaPublish(VideoConference):

    async def join(self, room: AnyStr):
        data = dict(request="join", ptype="publisher", display=self.username, room=room, id=self.uid)
        payload = {"body": data}
        response = await self.send(payload)
        return response["plugindata"]["data"]["publishers"]

    async def create_and_join(self, room: AnyStr, room_data: Optional[Dict[AnyStr, Any]] = None):
        await self.create(room, room_data)
        return await self.join(room)

    async def publish(self, offer, payload):
        request = {"request": "publish"}
        JSEP = {
            "sdp": offer["sdp"],
            "type": offer["type"]
        }
        if payload:
            request.update(payload)

        data = {
            "body": request,
            "jsep": JSEP
        }
        response = await self.send(data)
        self.emit("answer", response["jsep"])
        return response["plugindata"]["data"]["publishers"][0], response["jsep"]

    async def configure(self, offer, payload: dict = None):
        request = {"request": "configure"}
        JSEP = {
            "sdp": offer["sdp"],
            "type": offer["type"]
        }
        if payload:
            request.update(payload)

        data = {
            "body": request,
            "jsep": JSEP
        }
        return await self.send(data)

    async def unpublish(self):
        request = {"request": "unpublish"}
        response = await self.send({"body": request})
        return response["plugindata"]["data"]
