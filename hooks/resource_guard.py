"""af.resource_guard hook — pre-send resource checks.

Phase: pre_send
Priority: 101
Trigger: af-related operations
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any


@dataclass
class HookResult:
    success: bool
    message: str = ""
    data: Any = None


async def resource_guard_hook(event: dict, forge: Any) -> HookResult:
    """Check resource limits before allowing af operations."""
    operation = event.get("operation", "")

    if operation == "spawn":
        try:
            forge.guard.check_agent_limit(len(forge.list_agents()))
        except forge.guard.LimitExceeded as e:
            return HookResult(success=False, message=str(e))

    elif operation == "message":
        agent_name = event.get("agent_name", "")
        try:
            instance = forge.instances.get(agent_name)
            max_concurrent = instance.limits.get("max_concurrent", 3)
            current = event.get("current_concurrent", 0)
            forge.guard.check_concurrent(agent_name, current, max_concurrent)
        except (KeyError, forge.guard.LimitExceeded) as e:
            return HookResult(success=False, message=str(e))

    return HookResult(success=True, message="Resource check passed")
