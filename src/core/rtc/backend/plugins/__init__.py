import typing
from core.rtc.backend.connection.session import JanusSession
from core.rtc.backend.connection.socket import logger


class JanusPlugin:

    def __init__(self, session: JanusSession, plugin_id: typing.AnyStr):
        self._id = plugin_id
        self._session = session

    async def emit(self, _: typing.Dict):
        logger.info("Sending message to the plugin")
        """ Sends message to the plugin handle """
        raise NotImplementedError("emit method implemented. implement emit method")

    async def send(self, message):
        return await self.emit(message)

    async def trickle(self, candidates: typing.List[typing.Dict[typing.AnyStr, typing.Any]]):
        message = {"janus": "trickle", "handle_id": self._id, "candidates": candidates}
        return await self.send(message)

    async def complete_trickle(self):
        message = {"janus": "trickle", "handle_id": self._id, "candidate": "completed"}
        return await self.send(message)
