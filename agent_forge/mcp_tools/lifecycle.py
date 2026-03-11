from __future__ import annotations
from typing import Any
from agent_forge.core import AgentForge
from agent_forge.models import AgentInstance


def _instance_to_dict(inst: AgentInstance) -> dict[str, Any]:
    return {
        "agent_name": inst.agent_name,
        "template_id": inst.template_id,
        "status": inst.status.value,
        "rooms": inst.rooms,
        "config": inst.config,
        "limits": inst.limits,
        "created_at": inst.created_at,
        "last_active_at": inst.last_active_at,
    }


def _spawn_agent(
    forge: AgentForge,
    template_id: str,
    agent_name: str,
    rooms: list[str] | None = None,
    config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    try:
        inst = forge.spawn(template_id, agent_name, rooms)
        return _instance_to_dict(inst)
    except (KeyError, ValueError) as e:
        return {"error": str(e)}


def _destroy_agent(forge: AgentForge, agent_name: str) -> dict[str, Any]:
    try:
        forge.destroy(agent_name)
        target = next((i for i in forge.instances.list() if i.agent_name == agent_name), None)
        if target:
            return _instance_to_dict(target)
        return {"agent_name": agent_name, "status": "destroyed"}
    except (KeyError, Exception) as e:
        return {"error": str(e)}


def _sleep_agent(forge: AgentForge, agent_name: str) -> dict[str, Any]:
    try:
        forge.sleep(agent_name)
        inst = forge.instances.get(agent_name)
        return _instance_to_dict(inst)
    except (KeyError, Exception) as e:
        return {"error": str(e)}


def _wake_agent(forge: AgentForge, agent_name: str) -> dict[str, Any]:
    try:
        forge.wake(agent_name)
        inst = forge.instances.get(agent_name)
        return _instance_to_dict(inst)
    except (KeyError, Exception) as e:
        return {"error": str(e)}


def _list_agents(
    forge: AgentForge, status: str | None = None
) -> list[dict[str, Any]]:
    from agent_forge.models import AgentStatus
    s = AgentStatus(status) if status else None
    return [_instance_to_dict(i) for i in forge.list_agents(s)]


def _get_agent(forge: AgentForge, agent_name: str) -> dict[str, Any]:
    try:
        inst = forge.instances.get(agent_name)
        return _instance_to_dict(inst)
    except KeyError as e:
        return {"error": str(e)}


def register_lifecycle_tools(server, forge: AgentForge):
    """Register all 6 lifecycle tools on the MCP server."""

    @server.tool()
    async def spawn_agent(
        template_id: str,
        agent_name: str,
        rooms: list[str] | None = None,
    ) -> str:
        """Create and activate an agent from a template.

        Args:
            template_id: ID of the template to use (e.g. "code-reviewer")
            agent_name: Unique name for the new agent instance
            rooms: Optional list of room IDs to join
        """
        import json
        result = _spawn_agent(forge, template_id, agent_name, rooms)
        return json.dumps(result, ensure_ascii=False)

    @server.tool()
    async def destroy_agent(agent_name: str) -> str:
        """Permanently destroy an agent instance.

        Args:
            agent_name: Name of the agent to destroy
        """
        import json
        return json.dumps(_destroy_agent(forge, agent_name), ensure_ascii=False)

    @server.tool()
    async def sleep_agent(agent_name: str) -> str:
        """Put an active agent to sleep (hibernation).

        Args:
            agent_name: Name of the agent to sleep
        """
        import json
        return json.dumps(_sleep_agent(forge, agent_name), ensure_ascii=False)

    @server.tool()
    async def wake_agent(agent_name: str) -> str:
        """Wake a sleeping agent back to active state.

        Args:
            agent_name: Name of the agent to wake
        """
        import json
        return json.dumps(_wake_agent(forge, agent_name), ensure_ascii=False)

    @server.tool()
    async def list_agents(status: str | None = None) -> str:
        """List all agent instances, optionally filtered by status.

        Args:
            status: Filter by status: "active", "sleeping", "created", "destroyed"
        """
        import json
        return json.dumps(_list_agents(forge, status), ensure_ascii=False)

    @server.tool()
    async def get_agent(agent_name: str) -> str:
        """Get detailed information about a specific agent.

        Args:
            agent_name: Name of the agent to look up
        """
        import json
        return json.dumps(_get_agent(forge, agent_name), ensure_ascii=False)
