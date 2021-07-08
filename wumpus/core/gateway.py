import sys
import asyncio

from enums import OpCode
from aiohttp import ClientWebSocketResponse


__all__ = (
    'Websocket',
    'HeartbeatManager',
    'Gateway'
)


class Websocket(ClientWebSocketResponse):
    """
    Represents a websocket connection to Discord's gateway.
    """



class HeartbeatManager:
    """
    Manages and acks heartbeats from and to Discord's gateway.
    """
    
# now tell r we gonna have a _connection or not :C
# connection is retrieved from gateway.connection  right(?)
# oh ok then
    __slots__ = ('_gateway', '_connection', 'acked')

    def __init__(self, gateway, connection, /) -> None:
        self._gateway = gateway
        self._connection = gateway.connection
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
                await self._ws.reconnect()
                self.stop()
            await asyncio.sleep(self._gateway.heartbeat_interval)


    

class Gateway:
    """
    Represents the gateway clients use.
    """

    __slots__ = ('heartbeat_interval',)
    
    @classmethod
    async def connect_from_client(cls, client):
        """
        Create a Gateway object from client
        """
        cls()
        # TODO: Add all the attributes needed here
        # Stuff here means that it will stay as it is for the whole time

        await self.connect()
    
    async def connect(self):
        # Stuff here means they will need to be changed everytime it reconnect
        self.ws = await self._connection.session.ws_connect(self.gateway)
        await self.receive_event()
    
    

    
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
    
    async def reconnect_gateway(self, code: int):
        await self.ws.close(4000)
    
    async def receive_events(self): ...# igtg
    # can you clone from github 
    # what 
    # you wont have access if i leave
    # so you have to clone from github 
    # fine bad # ok lemme just create repo and the nbyer
    # :ccc
    # make amogus repo when >:(