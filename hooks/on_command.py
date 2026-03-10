"""af.on_command hook — triggers on /af:* commands.

Phase: after_write
Priority: 110
Trigger: ext.command.ns == 'af'
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any


@dataclass
class HookResult:
    success: bool
    message: str = ""
    data: Any = None


async def on_command(event: dict, forge: Any) -> HookResult:
    """Handle /af:* commands dispatched via EXT-15 Command."""
    command = event.get("command", "")
    params = event.get("params", {})

    if command == "spawn":
        template_id = params.get("template", "")
        agent_name = params.get("name", "")
        rooms = params.get("rooms", [])
        instance = forge.spawn(template_id, agent_name, rooms)
        return HookResult(success=True, message=f"Agent '{agent_name}' spawned", data={"agent": instance.agent_name})

    elif command == "destroy":
        forge.destroy(params.get("name", ""))
        return HookResult(success=True, message=f"Agent '{params.get('name')}' destroyed")

    elif command == "list":
        agents = forge.list_agents()
        return HookResult(success=True, data={"agents": [a.agent_name for a in agents]})

    elif command == "wake":
        forge.wake(params.get("name", ""))
        return HookResult(success=True, message=f"Agent '{params.get('name')}' woken")

    elif command == "sleep":
        forge.sleep(params.get("name", ""))
        return HookResult(success=True, message=f"Agent '{params.get('name')}' sleeping")

    elif command == "templates":
        templates = forge.templates.list()
        return HookResult(success=True, data={"templates": [t.id for t in templates]})

    return HookResult(success=False, message=f"Unknown command: {command}")
