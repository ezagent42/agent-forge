# src/adapters/protocol.py
from __future__ import annotations
from typing import Any, AsyncIterator, Protocol, runtime_checkable
from agent_forge.models import AgentMessage, AgentContext, AgentChunk, AgentCapabilities


@runtime_checkable
class AgentAdapter(Protocol):
    async def handle_message(
        self, message: AgentMessage, context: AgentContext
    ) -> AsyncIterator[AgentChunk]: ...

    async def handle_tool_result(
        self, tool_use_id: str, result: Any
    ) -> AsyncIterator[AgentChunk]: ...

    def capabilities(self) -> AgentCapabilities: ...
