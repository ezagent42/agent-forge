# tests/test_adapters.py
import asyncio
from agent_forge.adapters.protocol import AgentAdapter
from agent_forge.adapters.base import BaseAdapter
from agent_forge.models import (
    AgentMessage, AgentContext, AgentChunk, AgentCapabilities,
)


def test_base_adapter_is_agent_adapter():
    """BaseAdapter must implement AgentAdapter protocol."""
    assert issubclass(BaseAdapter, AgentAdapter) or hasattr(BaseAdapter, "handle_message")


class EchoAdapter(BaseAdapter):
    """Test adapter that echoes input."""
    async def _generate(self, message: AgentMessage, context: AgentContext):
        yield AgentChunk(type="text", content=f"Echo: {message.content}")
        yield AgentChunk(type="done", content=None)

    def capabilities(self) -> AgentCapabilities:
        return AgentCapabilities(streaming=True, tool_use=False)


def test_echo_adapter_handle_message():
    adapter = EchoAdapter(config={})
    msg = AgentMessage(content="hello", author="@alice:r", room_id="r1", ref_id="ref1")
    ctx = AgentContext(system_prompt="You are a test bot.")

    chunks = []
    async def collect():
        async for chunk in adapter.handle_message(msg, ctx):
            chunks.append(chunk)

    asyncio.run(collect())
    assert len(chunks) == 2
    assert chunks[0].type == "text"
    assert chunks[0].content == "Echo: hello"
    assert chunks[1].type == "done"


def test_adapter_capabilities():
    adapter = EchoAdapter(config={})
    caps = adapter.capabilities()
    assert caps.streaming is True
    assert caps.tool_use is False
