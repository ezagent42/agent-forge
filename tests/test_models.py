# tests/test_models.py
from agent_forge.models import (
    AgentStatus, AgentTemplate, AgentInstance,
    AgentMessage, AgentContext, AgentChunk, AgentCapabilities,
)


def test_agent_status_enum():
    assert AgentStatus.CREATED.value == "created"
    assert AgentStatus.ACTIVE.value == "active"
    assert AgentStatus.SLEEPING.value == "sleeping"
    assert AgentStatus.DESTROYED.value == "destroyed"


def test_agent_template_creation():
    t = AgentTemplate(
        id="code-reviewer",
        name="Code Reviewer",
        adapter="claude-code",
        config={"model": "sonnet", "allowed_tools": ["Read", "Search"]},
        default_role="af:agent",
        soul_template="# Review Bot\nYou are a code reviewer.",
        description="Reviews code for quality and security.",
    )
    assert t.id == "code-reviewer"
    assert t.adapter == "claude-code"


def test_agent_instance_creation():
    inst = AgentInstance(
        agent_name="review-bot",
        template_id="code-reviewer",
        status=AgentStatus.CREATED,
        rooms=[],
        config={"model": "sonnet"},
        limits={"max_concurrent": 3, "api_budget_daily": 500},
        lifecycle={"auto_start": True, "idle_timeout": "1h", "auto_wake_on_mention": True},
    )
    assert inst.status == AgentStatus.CREATED
    assert inst.limits["max_concurrent"] == 3


def test_agent_message():
    msg = AgentMessage(
        content="check PR #501",
        author="@alice:relay-a.example.com",
        room_id="room-123",
        ref_id="ref-456",
    )
    assert msg.author.startswith("@alice")


def test_agent_chunk_types():
    text_chunk = AgentChunk(type="text", content="Hello")
    done_chunk = AgentChunk(type="done", content=None)
    assert text_chunk.type == "text"
    assert done_chunk.type == "done"
