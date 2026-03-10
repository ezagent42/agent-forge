"""af.on_mention hook — triggers when @agent is mentioned.

Phase: after_write
Priority: 105
Trigger: timeline_index.insert + body contains @agent
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any


@dataclass
class HookResult:
    success: bool
    message: str = ""
    data: Any = None


async def on_mention(event: dict, forge: Any) -> HookResult:
    """Handle @agent mentions in messages."""
    body = event.get("body", "")
    mentioned_agents = event.get("mentioned_agents", [])

    for agent_name in mentioned_agents:
        try:
            instance = forge.instances.get(agent_name)
        except KeyError:
            continue

        if instance.status.value not in ("active", "sleeping"):
            continue

        # If sleeping, auto_wake hook will handle wake-up
        # Build context and dispatch to adapter
        # (Adapter integration deferred to Engine Phase 1)

    return HookResult(success=True, message=f"Mention processed for {len(mentioned_agents)} agents")
