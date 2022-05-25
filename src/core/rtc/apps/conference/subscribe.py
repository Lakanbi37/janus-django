from typing import Optional, Dict, AnyStr, List, Any
from core.rtc.apps.conference import VideoConference


class MediaSubscribe(VideoConference):

    async def join(self, room: AnyStr,
                   streams: Optional[List[Dict[AnyStr, AnyStr]]] = None,
                   props: Optional[Dict] = None):
        request = {
            "request": "join",
            "ptype": "subscriber",
            "room": room,
            "streams": streams
        }
        request.update(props)
        data = {
            "body": request
        }
        resp = await self.send(data)
        self.emit("offer", resp["jsep"])
        return resp["jsep"]

    async def watch(self, jsep: Dict):
        request = {
            "body": {
                "request": "start"
            },
            "jsep": {
                "sdp": jsep["sdp"],
                "type": jsep["type"]
            }
        }
        response = await self.send(request)
        self.emit("event", "Watching...")
        return response["plugindata"]["data"]

    async def unsubscribe(self, streams: List[Dict[AnyStr, Any]]):
        request = {
            "body": {
                "request": "unsubscribe",
                "streams": streams
            }
        }
        response = await self.send(request)
        self.emit("offer", response["jsep"])
        return response["jsep"]

    async def subscribe(self, streams: List[Dict[AnyStr, Any]]):
        request = {
            "body": {
                "request": "subscribe",
                "streams": streams,
            }
        }
        response = await self.send(request)
        self.emit("offer", response["jsep"])
        return response["jsep"]

    async def pause(self):
        request = {
            "body": {
                "request": "pause"
            }
        }
        response = await self.send(request)
        return response["plugindata"]["data"]

    async def resume(self):
        request = {
            "body": {
                "request": "start"
            }
        }
        response = await self.send(request)
        return response["plugindata"]["data"]

    async def configure(self, payload: Dict[AnyStr, Any]):
        body = {
            "request": "configure"
        }
        body.update(payload)
        request = {
            "body": body
        }
        response = await self.send(request)
        return response

    async def leave(self):
        request = {
            "body": {
                "request": "leave"
            }
        }
        response = await self.send(request)
        return response
