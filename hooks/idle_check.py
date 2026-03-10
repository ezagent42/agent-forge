"""af.idle_check hook — periodic check for idle agents.

Phase: periodic (every 5 minutes)
Priority: 100
Trigger: timer
"""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any


@dataclass
class HookResult:
    success: bool
    message: str = ""
    data: Any = None


def _parse_timeout(timeout_str: str) -> int:
    """Parse timeout string like '1h', '30m' to seconds."""
    if timeout_str.endswith("h"):
        return int(timeout_str[:-1]) * 3600
    if timeout_str.endswith("m"):
        return int(timeout_str[:-1]) * 60
    return int(timeout_str)


async def idle_check(event: dict, forge: Any) -> HookResult:
    """Check for idle agents and put them to sleep."""
    now = datetime.now(timezone.utc)
    slept = []

    for instance in forge.list_agents():
        if instance.status.value != "active":
            continue

        timeout_str = instance.lifecycle.get("idle_timeout", "1h")
        timeout_secs = _parse_timeout(timeout_str)

        if instance.last_active_at:
            last_active = datetime.fromisoformat(instance.last_active_at)
            idle_secs = (now - last_active).total_seconds()
            if idle_secs > timeout_secs:
                forge.sleep(instance.agent_name)
                slept.append(instance.agent_name)

    return HookResult(success=True, message=f"Idle check: {len(slept)} agents sleeping", data={"slept": slept})
