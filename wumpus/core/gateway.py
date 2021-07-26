from __future__ import annotations

import asyncio
import json
import sys
import zlib
from typing import Optional, Union

import aiohttp
import earl

from ..typings import JSON
from ..utils import Ratelimiter
from .connection import Connection, GatewayInfo
from .enums import OpCode
from .events import EventEmitter

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
            'op': OpCode.heartbeat.value,
            'd': self._gateway._seq,
        }
        await self._gateway.send(payload, force=True) # Heartbeat should be send no matter what.

    async def heartbeat_task(self) -> None:
        while not self._connection.closed:
            await self._gateway.heartbeat()
            try:
                await asyncio.wait_for(self.acked, timeout=3)
            except asyncio.TimeoutError:
                await self.stop()
                raise Reconnect()
            await asyncio.sleep(self._gateway.heartbeat_interval)


class Gateway:
    """
    Represents the gateway clients use.
    """

    # __slots__ = ('heartbeat_interval', 'ws', 'gateway', '_connection', '_keep_alive', '_inflator', '_buffer')
    
    def __init__(self, ws: aiohttp.ClientWebSocketResponse, /) -> None:
        self._ws: aiohttp.ClientWebSocketResponse = ws
        self._hearbeat_manager: HeartbeatManager = None
        self._connection: Connection = None

        self._info: GatewayInfo = None
        self._inflator = zlib.decompressobj()
        self._buffer = bytearray()
        self._sequence: int = None
        self._session_id: int = None

        self.__token: str = None
        
        self.shard_id: Optional[int] = None        
        self.shard_count: Optional[int] = None        
        self.heartbeat_interval: int = None
        self._ratelimiter: Ratelimiter = None

        self._emitter: EventEmitter = EventEmitter(self)

    @classmethod
    async def from_connection(
        cls,
        connection: Connection,
        /,
        *,
        session_id: Optional[int] = None, 
        sequence: Optional[int] =  None, 
        resume: bool = True
    ):
        """
        Creates a :class:`Gateway` from a :class:`Connection`.
        """

        gateway_info = await connection.get_gateway_bot()
        ws = await connection.http.session.ws_connect(gateway_info.url + "?v=9&encoding=etf&compress=zlib-stream")

        gateway = cls(ws)
        gateway.__token = connection.token
        gateway._connection = connection
        await gateway.receive_events()  # For Hello event

        gateway.shard_id = connection.shard_id
        gateway.shard_count = connection.shard_count
        gateway._session_id = session_id
        gateway._sequence = sequence
        gateway._ratelimiter = Ratelimiter(110, 60, gateway.gateway_ratelimited()) # Reserve 10 for heartbeat.

        if resume:
            await gateway.resume()
            return gateway
        
        await gateway.identify()
        return gateway

    async def send(self, payload: JSON, *, force: bool = False) -> None:
        if force:
            return await self._ws.send_str(json.dumps(payload))

        async with self._ratelimiter:
            return await self._ws.send_str(json.dumps(payload))
    
    async def gateway_ratelimited(self) -> None:
        ...
    
    async def identify(self, /) -> None:
        payload = {
            "op": OpCode.identify.value,
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
    
        await self.send(payload)
    
    async def resume(self) -> None:
        payload = {
            'op': OpCode.resume.value,
            'd': {
                'seq': self._seq,
                'session_id': self._session_id,
                'token': self.__token,
            }
        }
        await self.send(payload)
    
    async def parse_websocket_message(self, data: Union[str, bytes]) -> None:
        if type(data) is bytes:
            self._buffer.extend(data)
            if len(data) < 4 or data[-4:] != b'\x00\x00\xff\xff':
                return

            data = self._inflator.decompress(self._buffer)
            self._buffer = bytearray()

        message = earl.unpack(data)
        op = OpCode(message.get('op'))
        data = message.get('d')
        seq = message.get('s')

        if seq is not None:
            self._seq = seq

        if op is OpCode.reconnect:
            raise Reconnect()

        elif op is OpCode.heartbeat_ack:
            self._keep_alive.ack()

        elif op is OpCode.heartbeat:
            await self._keep_alive.heartbeat()

        elif op is OpCode.hello:
            self.heartbeat_interval = data['heartbeat_interval'] / 1000  # For seconds
            self._keep_alive = HeartbeatManager(self)
            await self._keep_alive.heartbeat()

        elif op is OpCode.invalidate_session:
            if data is not True:
                # We need to send a fresh Identify
                self._seq = None
                self._session_id = None
                raise Reconnect(resume=False)
            raise Reconnect()

        elif op is OpCode.dispatch:
            event = message.get('t')
            return self._emitter.handle(event, data)

        else: 
            raise ...
    
    async def receive_events(self):
        m = await self._ws.receive()
        if m.type is aiohttp.WSMsgType.TEXT or m.type is aiohttp.WSMsgType.BINARY:
            await self.parse_websocket_message(m.data)
        elif m.type is aiohttp.WSMsgType.ERROR:
            raise m.data
        elif m.type in (aiohttp.WSMsgType.CLOSED, aiohttp.WSMsgType.CLOSING, aiohttp.WSMsgType.CLOSE):
            raise Reconnect()
