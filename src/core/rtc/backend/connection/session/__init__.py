import typing
from pyee.asyncio import AsyncIOEventEmitter


class JanusSession(AsyncIOEventEmitter):
    def __init__(self, url: typing.AnyStr, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._url = url
        self._plugins = {}
        self._session_id = None

    async def send(self, message: typing.Dict):
        """"Sends message to the janus server instance"""
        raise NotImplementedError("{} instance must implement a 'send' method" % self.__class__.__name__)

    async def create(self):
        """
        Create a session in the janus server instance. \n
        Method must be implemented
        """
        raise NotImplementedError("{} instance must implement a 'create' method" % self.__class__.__name__)

    async def attach(self, plugin_name: typing.AnyStr):
        """"Attach a new plugin to the janus session"""
        raise NotImplementedError("{} instance must implement an 'attach' method" % self.__class__.__name__)

    async def destroy(self):
        """"closes the janus session"""
        raise NotImplementedError("{} instance must implement a 'destroy' method" % self.__class__.__name__)
