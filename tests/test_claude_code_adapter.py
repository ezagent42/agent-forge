import asyncio
from unittest.mock import AsyncMock, MagicMock
from agent_forge.adapters.claude_code import ClaudeCodeAdapter
from agent_forge.models import AgentMessage, AgentContext, AgentChunk


def test_capabilities():
    adapter = ClaudeCodeAdapter(config={"model": "sonnet", "api_key": "test"})
    caps = adapter.capabilities()
    assert caps.streaming is True
    assert caps.tool_use is True


def test_handle_message_streaming():
    adapter = ClaudeCodeAdapter(config={"model": "sonnet", "api_key": "test"})
    msg = AgentMessage(content="hello", author="@alice:r", room_id="r1", ref_id="ref1")
    ctx = AgentContext(system_prompt="You are a bot.")

    # Mock the _stream_api to return async iterator of event dicts
    async def mock_stream(*args, **kwargs):
        events = [
            {"type": "content_block_delta", "delta": {"text": "Hi "}},
            {"type": "content_block_delta", "delta": {"text": "there!"}},
            {"type": "message_stop"},
        ]
        for event in events:
            yield event

    chunks = []
    async def collect():
        adapter._stream_api = lambda *a, **kw: mock_stream()
        async for chunk in adapter.handle_message(msg, ctx):
            chunks.append(chunk)

    asyncio.run(collect())
    text_chunks = [c for c in chunks if c.type == "text"]
    assert len(text_chunks) >= 1
    done_chunks = [c for c in chunks if c.type == "done"]
    assert len(done_chunks) == 1
