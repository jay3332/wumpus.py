import sys
import zlib
import asyncio
import aiohttp
import json

from enums import OpCode
from typing import Union

from ..typings import JSON


__all__ = (
    'Websocket',
    'HeartbeatManager',
    'Gateway'
)


class Reconnect(Exception):
    pass

class HeartbeatManager:
    """
    Manages and acks heartbeats from and to Discord's gateway.
    """
    
# now tell r we gonna have a _connection or not :C
# connection is retrieved from gateway.connection  right(?)
# oh ok then
    __slots__ = ('_gateway', '_connection', 'acked', '__task')

    def __init__(self, gateway, /) -> None:
        self._gateway = gateway
        self._connection = gateway._connection
        self.acked = None
    
    def start(self) -> None:
        self.acked = self._connection.loop.create_future()
        self.__task = self._connection.loop.create_task(self.heartbeat())
    
    def ack(self) -> None:
        self.acked.set_result(True)
        self.acked = self._connection.loop.create_future()
    
    async def stop(self) -> None:
        self.__task.cancel()
        try:
            await self.__task
        except asyncio.CancelledError:
            pass

    async def heartbeat(self) -> None:
        while not self._connection.closed:
            await self._gateway.heartbeat()
            try:
                await asyncio.wait_for(self.acked, timeout=3)
            except asyncio.TimeoutError:
                self.stop()
                raise Reconnect()
            await asyncio.sleep(self._gateway.heartbeat_interval)


    

class Gateway:
    """
    Represents the gateway clients use.
    """

    __slots__ = ('heartbeat_interval', 'ws', 'gateway', '_connection', '_keep_alive', '_inflator', '_buffer')
    
    @classmethod
    async def connect_from_client(cls, client):
        """
        Create a Gateway object from client
        """
        self = cls()
        # TODO: Add all the attributes needed here
        # Stuff here means that it will stay as it is for the whole time
        self._inflator = zlib.decompressobj()
        while not self._connection.closed:
            try:
                await self.connect()
                while True:
                    await self.receive_event()
            except Reconnect:
                await self.ws.close(4000)
                continue
    
    async def connect(self):
        self.gateway = await self._connection.http.get_gateway_bot()
        self.ws = await self._connection.http.session.ws_connect(self.gateway)
        self._buffer = bytearray()
        self._keep_alive = HeartbeatManager(self)
        await self.receive_event() # For Hello event

    async def send_json(self, payload: JSON) -> None:
        await self.ws.send_str(json.dumps(payload))
    
    async def identify(self):
        payload = {
            "op": OpCode.IDENTIFY.value,
            "d": {
                "token": self.__token,
                "properties": {
                    "$os": sys.platform,
                    "$browser": "wumpus.py",
                    "$device": "wumpus.py",
                },
                "compress": True,
                "large_threshold": 250,
            }
        }
        if self.shard_id is not None and self.shard_count is not None:
            payload["d"]["shard"] = [self.shard_id, self.shard_count]

        # TODO: Implement presence thing

        # TODO: Implement intent thing
    
        await self.send_json(payload)
    
    async def received_events(self, data: Union[str, bytes]) -> None:
        if type(data) is bytes:
            self._buffer.extend(data)
            if len(data) < 4 or data[-4:] != b'\x00\x00\xff\xff':
                return
            data = self._inflator.decompress(self._buffer)
            self._buffer = bytearray()
        msg = json.loads(data)
        op = msg.get('op')
        data = msg.get('d')
        seq = msg.get('s')
        if seq is not None:
            self._seq = seq
        if op == OpCode.RECONNECT:
            raise Reconnect()



    
    async def receive_events(self):
        m = await self.ws.receive()
        if msg.type is aiohttp.WSMsgType.TEXT or msg.type is aiohttp.WSMsgType.BINARY:
            await self.received_events(m.data)
        elif msg.type is aiohttp.WSMsgType.ERROR:
            raise msg.data
        elif m.type in (aiohttp.WSMsgType.CLOSED, aiohttp.WSMsgType.CLOSING, aiohttp.WSMsgType.CLOSE):
            raise Reconnect()