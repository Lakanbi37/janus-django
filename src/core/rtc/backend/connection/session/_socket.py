import asyncio
import typing
from core.rtc.backend.connection.socket import SocketConnectionClient, logger
from core.rtc.backend.plugins import JanusPlugin
from core.rtc.backend.connection.session import JanusSession


class JanusSocketSession(JanusSession):
    def __init__(self, *args, **kwargs):
        self._ws: typing.Optional[SocketConnectionClient] = None
        self._ka_interval = 15
        self._ka_task = None

        super(JanusSocketSession, self).__init__(*args, **kwargs)

    async def send(self, message: typing.Dict):
        message.update({"session_id": self._session_id})
        return await self._ws.send(message)

    async def create(self):
        logger.info("Creating Session")
        self._ws = await SocketConnectionClient(url=self._url).connect()
        message = {"janus": "create"}
        response = await self.send(message)
        assert response["janus"] == "success"
        self._session_id = response["data"]["id"]
        self._ka_task = asyncio.ensure_future(self._keep_alive())

        @self._ws.on("event")
        async def on_event(event):
            print(event)
            self.emit("event", event)

        logger.info("Session created")

    async def attach(self, plugin_name: typing.AnyStr):
        logger.info('Attaching plugin {}' % plugin_name)
        message = {'janus': 'attach', 'plugin': plugin_name}
        response = await self.send(message)
        assert response['janus'] == 'success'
        plugin_id = response['data']['id']
        plugin = JanusPlugin(plugin_id=plugin_id, session=self)
        self._plugins[plugin_id] = plugin
        logger.info("Plugin {0} {1} Attached" % plugin_name, plugin_id)
        return plugin

    async def _keep_alive(self):
        while True:
            logger.info('Sending keepalive')
            message = {'janus': 'keepalive'}
            await self.send(message)
            logger.info('Keepalive OK')
            await asyncio.sleep(self._ka_interval)

    async def destroy(self):
        logger.info('Destroying session')
        if self._session_id:
            message = {'janus': 'destroy'}
            await self.send(message)
            self._session_id = None
        if self._ka_task:
            self._ka_task.cancel()
            try:
                await self._ka_task
            except asyncio.CancelledError:
                pass
            self._ka_task = None
        self._plugins = {}
        logger.info('Session destroyed')
        logger.info('Closing WebSocket')
        if self._ws:
            await self._ws.close()
            self._ws = None
