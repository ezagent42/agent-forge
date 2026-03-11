from __future__ import annotations
from typing import Any
from agent_forge.core import AgentForge
from agent_forge.models import AgentStatus


def _chat(
    forge: AgentForge,
    agent_name: str,
    message: str,
    context: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    try:
        inst = forge.instances.get(agent_name)
    except KeyError:
        return {"error": f"Agent '{agent_name}' not found"}

    if inst.status != AgentStatus.ACTIVE:
        return {"error": f"Agent '{agent_name}' is not active (status: {inst.status.value})"}

    template = forge.templates.get(inst.template_id)

    return {
        "agent_name": agent_name,
        "template_id": inst.template_id,
        "message_received": message,
        "reply": f"[{template.name}] Adapter '{template.adapter}' not yet connected. "
                 f"Message queued: {message[:100]}",
        "adapter": template.adapter,
        "status": "pending_adapter",
    }


def register_chat_tools(server, forge: AgentForge):
    """Register chat tool on the MCP server."""

    @server.tool()
    async def chat(
        agent_name: str,
        message: str,
        context: list[dict[str, str]] | None = None,
    ) -> str:
        """Send a message to an agent and get a reply.

        Args:
            agent_name: Name of the target agent (must be active)
            message: The message content to send
            context: Optional conversation context as list of {role, content} dicts
        """
        import json
        return json.dumps(
            _chat(forge, agent_name, message, context), ensure_ascii=False
        )
