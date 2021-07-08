import sys
import json
import zlib
import asyncio
import aiohttp

from enums import OpCode
from typing import Union, Optional, Dict

from ..typings import JSON


__all__ = (
    'Reconnect',
    'HeartbeatManager',
    'Gateway'
)


class Reconnect(Exception):
    def __init__(self, resume=True):
        self.resume = resume

class HeartbeatManager:
    """
    Manages and acks heartbeats from and to Discord's gateway.
    """
    
    __slots__ = ('_gateway', '_connection', 'acked', '__task')

    def __init__(self, gateway: Gateway, /) -> None:
        self._gateway = gateway
        self._connection = gateway._connection
        self.acked = self._connection.loop.create_future()
    
    def start(self) -> None:
        self.acked = self._connection.loop.create_future()
        self.__task = self._connection.loop.create_task(self.heartbeat_task())
    
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
        payload = {
            'op': OpCode.HEARTBEAT.value,
            'd': self._gateway._seq,
        }
        await self._gateway.send_json(payload)

    async def heartbeat_task(self) -> None:
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

    # __slots__ = ('heartbeat_interval', 'ws', 'gateway', '_connection', '_keep_alive', '_inflator', '_buffer')
    
    def __init__(self, ws: aiohttp.ClientWebSocketResponse) -> None:
        self._ws = ws
        self._inflator = zlib.decompressobj()
        self._buffer = bytearray()
        self._keep_alive = None
        self._seq = None
        self._session_id = None
        self.__token = None

    @classmethod
    async def connect_from_client(cls, client, *, session_id: Optional[int]=None, seq: Optional[int]=None, resume: bool=True):
        """
        Create a Gateway object from client
        """
        _gateway = await client._connection.http.get_gateway_bot()
        ws = await client._connection.http.session.ws_connect(_gateway)
        gateway = cls(ws)
        gateway.__token = client._connection.__token
        await gateway.receive_events() # For Hello event
        gateway.gateway = gateway
        gateway.shard_id = client._connection.shard_id
        gateway.shard_count = client._connection.shard_count
        gateway._session_id = session_id
        gateway._seq = seq

        if resume:
            await gateway.resume()
            return gateway
        
        await gateway.identify()

        return gateway

    async def send_json(self, payload: JSON) -> None:
        await self._ws.send_str(json.dumps(payload))
    
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
    
    async def resume(self) -> None:
        payload = {
            'op': OpCode.RESUME.value,
            'd': {
                'seq': self._seq,
                'session_id': self._session_id,
                'token': self.__token,
            }
        }
        await self.send_json(payload)
    
    async def received_events(self, data: Union[str, bytes]) -> None:
        if type(data) is bytes:
            self._buffer.extend(data)
            if len(data) < 4 or data[-4:] != b'\x00\x00\xff\xff':
                return
            data = self._inflator.decompress(self._buffer)
            self._buffer = bytearray()
        msg = json.loads(data)
        op = OpCode(msg.get('op'))
        data: Dict[str, Union[int, str]] = msg.get('d')
        seq = msg.get('s')
        if seq is not None:
            self._seq = seq
        if op is OpCode.RECONNECT:
            raise Reconnect()
        elif op is OpCode.HEARTBEAT_ACK:
            self._keep_alive.ack()
        elif op is OpCode.HEARTBEAT:
            await self._keep_alive.heartbeat()
        elif op is OpCode.HELLO:
            self.heartbeat_interval = data['heartbeat_interval'] / 1000 # For seconds
            self._keep_alive = HeartbeatManager(self)
            await self._keep_alive.heartbeat()
        elif op is OpCode.INVALIDATE_SESSION:
            if data is not True:
                # We need to send a fresh Identify
                self._seq = None
                self._session_id = None
                raise Reconnect(resume=False)
            raise Reconnect()
        elif op is OpCode.DISPATCH:
            event = msg.get('t')
            if event == "READY":
                self._session_id == data.get('session_id')
                # TODO: Handle user and application info
        else:
            raise ...



    
    async def receive_events(self):
        m = await self._ws.receive()
        if m.type is aiohttp.WSMsgType.TEXT or m.type is aiohttp.WSMsgType.BINARY:
            await self.received_events(m.data)
        elif m.type is aiohttp.WSMsgType.ERROR:
            raise m.data
        elif m.type in (aiohttp.WSMsgType.CLOSED, aiohttp.WSMsgType.CLOSING, aiohttp.WSMsgType.CLOSE):
            raise Reconnect()
