from typing import Any, Dict, Tuple

from .gateway import Gateway
from .connection import Connection

from ..typings import JSON
from ..typings.payloads import (
    ReadyEventPayload
)


__all__ = (
    'EventEmitter',
)


class _BaseEventEmitter:
    def __init__(self, gateway: Gateway, /) -> None:
        self._gateway: Gateway = gateway
 
    @property
    def _connection(self):
        return self._gateway._connection

    def handle(self, event: str, /, data: JSON) -> None:
        event = event.lower()

        if hasattr(self, event):
            coro = getattr(self, event)(data)
            self._connection.loop.create_task(coro)


class EventEmitter(_BaseEventEmitter):
    # TODO: Make JSON typehint TypedDicts

    async def ready(self, data: ReadyEventPayload, /) -> None:
        self._connection.patch_current_user(data['user'])
        self._connection.ws._session_id = data['session_id']

    async def message_create(self, data: JSON, /) -> None:
        ...
    
    async def resumed(self, data: JSON, /) -> None:
        ... 
        
    async def reconnect(self, data: JSON, /) -> None:
        ...
    
    async def invalid_session(self, data: JSON, /) -> None:
        ...
    
    async def application_command_create(self, data: JSON, /) -> None:
        ...
    
    async def application_command_update(self, data: JSON, /) -> None:
        ...
    
    async def application_command_delete(self, data: JSON, /) -> None:
        ...
    
    async def channel_create(self, data: JSON, /) -> None:
        ...

    async def channel_update(self, data: JSON, /) -> None:
        ...

    async def channel_delete(self, data: JSON, /) -> None:
        ...
    
    async def channel_pins_update(self, data: JSON, /) -> None:
        ...
    
    async def thread_create(self, data: JSON, /) -> None:
        ...
    
    async def thread_update(self, data: JSON, /) -> None:
        ...
    
    async def thread_delete(self, data: JSON, /) -> None:
        ...
    
    async def thread_list_sync(self, data: JSON, /) -> None:
        ...
    
    async def thread_member_update(self, data: JSON, /) -> None:
        ...
    
    async def thread_members_update(self, data: JSON, /) -> None:
        ...
    
    async def guild_create(self, data: JSON, /) -> None:
        ...
    
    async def guild_update(self, data: JSON, /) -> None:
        ...
    
    async def guild_delete(self, data: JSON, /) -> None:
        ...
    
    async def guild_ban_add(self, data: JSON, /) -> None:
        ...
    
    async def guild_ban_remove(self, data: JSON, /) -> None:
        ...
    
    async def guild_emojis_update(self, data: JSON, /) -> None:
        ...
    
    async def guild_integration_update(self, data: JSON, /) -> None:
        ...
    
    async def guild_member_add(self, data: JSON, /) -> None:
        ...
    
    async def guild_member_remove(self, data: JSON, /) -> None:
        ...
    
    async def guild_member_update(self, data: JSON, /) -> None:
        ...
    
    async def guild_members_chunk(self, data: JSON, /) -> None:
        ...
    
    async def guild_role_create(self, data: JSON, /) -> None:
        ...
    
    async def guild_role_update(self, data: JSON, /) -> None:
        ...
    
    async def guild_role_delete(self, data: JSON, /) -> None:
        ...
    
    async def integration_create(self, data: JSON, /) -> None:
        ...
    
    async def integration_update(self, data: JSON, /) -> None:
        ...
    
    async def integration_delete(self, data: JSON, /) -> None:
        ...
    
    async def interaction_create(self, data: JSON, /) -> None:
        ...
    
    async def invite_create(self, data: JSON, /) -> None:
        ...
    
    async def invite_delete(self, data: JSON, /) -> None:
        ...
    
    async def message_create(self, data: JSON, /) -> None:
        ...
    
    async def message_update(self, data: JSON, /) -> None:
        ...
    
    async def message_delete(self, data: JSON, /) -> None:
        ...
    
    async def message_delete_bulk(self, data: JSON, /) -> None:
        ...
    
    async def message_reaction_add(self, data: JSON, /) -> None:
        ...
    
    async def message_reaction_remove(self, data: JSON, /) -> None:
        ...
    
    async def message_reaction_remove_all(self, data: JSON, /) -> None:
        ...
    
    async def message_reaction_remove_emoji(self, data: JSON, /) -> None:
        ...
    
    async def presence_update(self, data: JSON, /) -> None:
        ...
    
    async def stage_instance_create(self, data: JSON, /) -> None:
        ...
    
    async def stage_instance_update(self, data: JSON, /) -> None:
        ...
    
    async def stage_instance_delete(self, data: JSON, /) -> None:
        ...
    
    async def typing_start(self, data: JSON, /) -> None:
        ...
    
    async def user_update(self, data: JSON, /) -> None:
        ...
    
    async def voice_state_update(self, data: JSON, /) -> None:
        ...
    
    async def voice_server_update(self, data: JSON, /) -> None:
        ...
    
    async def webhook_update(self, data: JSON, /) -> None:
        ...
