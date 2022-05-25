import typing
import asyncio
import logging
import json
import websockets as ws
from pyee.asyncio import AsyncIOEventEmitter

from core.exceptions import JanusError
from core.utils import transaction_id

logger = logging.getLogger("janus")


class SocketConnectionClient(AsyncIOEventEmitter):

    def __init__(self, url: typing.AnyStr, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.connection = None
        self._url = url
        self._transactions = {}

    async def connect(self):
        self.connection = await ws.connect(self._url, subprotocols=['janus-protocol'],
                                           ping_interval=10,
                                           ping_timeout=10,
                                           compression=None)
        if self.connection.open:
            asyncio.ensure_future(self.recv())
            logger.info("Connection Active")
            return self

    async def recv(self):
        try:
            async for message in self.connection:
                data = json.loads(message)
                tx_id = data.get("transaction")
                response = data["janus"]
                self.emit("event", data)

                # Handle ACK
                if tx_id and response == 'ack':
                    logger.debug(f'Received ACK for transaction {tx_id}')
                    if tx_id in self._transactions:
                        tx_in = self._transactions[tx_id]
                        if tx_in['request'] == 'keepalive':
                            tx = tx_in['tx']
                            tx.set_result(data)
                            del self._transactions[tx_id]
                            logger.debug(f'Closed transaction {tx_id}'
                                         f' with {response}')
                    continue
                # Handle Success / Event / Error
                if response not in {'success', 'error'}:
                    logger.info(f'Janus Event --> {response}')
                if tx_id and tx_id in self._transactions:
                    tx_in = self._transactions[tx_id]
                    tx = tx_in['tx']
                    tx.set_result(data)
                    del self._transactions[tx_id]
                    logger.debug(f'Closed transaction {tx_id}'
                                 f' with {response}')
        except JanusError:
            logger.error('WebSocket failure')
        logger.info('Connection closed')

    async def send(self, message: typing.Dict):
        tx_id = transaction_id(12)
        message.update({"transaction": tx_id})
        tx = asyncio.get_event_loop().create_future()
        tx_in = {"tx": tx, "request": message["janus"]}
        self._transactions[tx_id] = tx_in
        try:
            await asyncio.gather(self.connection.send(json.dumps(message)), tx)
        except Exception as e:
            tx.set_result(e)
        return tx.result()

    async def close(self):
        if self.connection:
            await self.connection.close()
            self.connection = None
        self._transactions = {}
