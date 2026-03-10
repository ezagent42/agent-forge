# src/models.py
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


class AgentStatus(Enum):
    CREATED = "created"
    ACTIVE = "active"
    SLEEPING = "sleeping"
    DESTROYED = "destroyed"


@dataclass
class AgentTemplate:
    id: str
    name: str
    adapter: str
    config: dict[str, Any]
    default_role: str
    soul_template: str
    description: str


@dataclass
class AgentInstance:
    agent_name: str
    template_id: str
    status: AgentStatus
    rooms: list[str] = field(default_factory=list)
    config: dict[str, Any] = field(default_factory=dict)
    limits: dict[str, Any] = field(default_factory=dict)
    lifecycle: dict[str, Any] = field(default_factory=dict)
    created_at: Optional[str] = None
    last_active_at: Optional[str] = None


@dataclass
class AgentMessage:
    content: str
    author: str
    room_id: str
    ref_id: str
    command: Optional[dict[str, Any]] = None


@dataclass
class ContextMessage:
    content: str
    author: str
    ref_id: str
    timestamp: str


@dataclass
class AgentContext:
    segment: list[ContextMessage] = field(default_factory=list)
    room_members: list[dict[str, Any]] = field(default_factory=list)
    working_dir: Optional[str] = None
    system_prompt: str = ""
    max_tokens: int = 4096


@dataclass
class AgentChunk:
    type: str  # "text" | "tool_use" | "tool_result" | "done" | "error"
    content: Any = None


@dataclass
class AgentCapabilities:
    streaming: bool = True
    tool_use: bool = False
    max_context_tokens: int = 8000
