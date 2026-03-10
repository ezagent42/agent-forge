"""af.auto_wake hook — auto-wakes sleeping agents on @mention.

Phase: after_write
Priority: 104
Trigger: Agent is SLEEPING + @mention + auto_wake_on_mention=true
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any


@dataclass
class HookResult:
    success: bool
    message: str = ""
    data: Any = None


async def auto_wake(event: dict, forge: Any) -> HookResult:
    """Auto-wake sleeping agents when mentioned."""
    agent_name = event.get("agent_name", "")

    try:
        instance = forge.instances.get(agent_name)
    except KeyError:
        return HookResult(success=False, message=f"Agent '{agent_name}' not found")

    if instance.status.value != "sleeping":
        return HookResult(success=False, message=f"Agent '{agent_name}' is not sleeping")

    auto_wake_enabled = instance.lifecycle.get("auto_wake_on_mention", False)
    if not auto_wake_enabled:
        return HookResult(success=False, message=f"Auto-wake disabled for '{agent_name}'")

    forge.wake(agent_name)
    return HookResult(success=True, message=f"Agent '{agent_name}' woken by mention")
