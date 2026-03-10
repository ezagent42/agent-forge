from __future__ import annotations
from typing import Any, AsyncIterator
from agent_forge.adapters.base import BaseAdapter
from agent_forge.models import (
    AgentMessage, AgentContext, AgentChunk, AgentCapabilities,
)


class ClaudeCodeAdapter(BaseAdapter):
    """Adapter that wraps the Anthropic Claude API with streaming support."""

    def __init__(self, config: dict[str, Any]):
        super().__init__(config)
        self.model = config.get("model", "sonnet")
        self.api_key = config.get("api_key", "")

    def capabilities(self) -> AgentCapabilities:
        return AgentCapabilities(streaming=True, tool_use=True, max_context_tokens=8000)

    async def _generate(
        self, message: AgentMessage, context: AgentContext
    ) -> AsyncIterator[AgentChunk]:
        """Stream response from Claude API."""
        messages = self._build_messages(message, context)

        async for event in self._stream_api(messages, context.system_prompt):
            event_type = event.get("type", "")

            if event_type == "content_block_delta":
                delta = event.get("delta", {})
                if "text" in delta:
                    yield AgentChunk(type="text", content=delta["text"])
                elif "tool_use" in delta:
                    yield AgentChunk(type="tool_use", content=delta["tool_use"])

            elif event_type == "message_stop":
                yield AgentChunk(type="done", content=None)

            elif event_type == "error":
                yield AgentChunk(type="error", content=event.get("error", "Unknown error"))

    def _build_messages(
        self, message: AgentMessage, context: AgentContext
    ) -> list[dict[str, str]]:
        """Build messages list from context segment + current message."""
        messages = []
        for ctx_msg in context.segment:
            role = "assistant" if ctx_msg.author.startswith("@agent") else "user"
            messages.append({"role": role, "content": ctx_msg.content})
        messages.append({"role": "user", "content": message.content})
        return messages

    async def _stream_api(
        self, messages: list[dict[str, str]], system_prompt: str
    ) -> AsyncIterator[dict]:
        """Stream from Anthropic API. Stub — requires anthropic SDK at runtime."""
        raise NotImplementedError(
            "ClaudeCodeAdapter._stream_api requires the anthropic SDK. "
            "This stub will be replaced when Engine Phase 1 is complete."
        )
