# src/adapters/base.py
from __future__ import annotations
from typing import Any, AsyncIterator
from agent_forge.models import (
    AgentMessage, AgentContext, AgentChunk, AgentCapabilities,
)


class BaseAdapter:
    def __init__(self, config: dict[str, Any]):
        self.config = config

    async def handle_message(
        self, message: AgentMessage, context: AgentContext
    ) -> AsyncIterator[AgentChunk]:
        async for chunk in self._generate(message, context):
            yield chunk

    async def _generate(
        self, message: AgentMessage, context: AgentContext
    ) -> AsyncIterator[AgentChunk]:
        raise NotImplementedError

    async def handle_tool_result(
        self, tool_use_id: str, result: Any
    ) -> AsyncIterator[AgentChunk]:
        yield AgentChunk(type="error", content="Tool use not supported by this adapter")

    def capabilities(self) -> AgentCapabilities:
        return AgentCapabilities()
