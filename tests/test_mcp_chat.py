import pytest
from pathlib import Path
from agent_forge.core import AgentForge
from agent_forge.models import AgentTemplate


@pytest.fixture
def forge(tmp_path):
    builtin_dir = tmp_path / "builtin"
    (builtin_dir / "templates").mkdir(parents=True)
    f = AgentForge(base_dir=builtin_dir)
    f.templates.register(AgentTemplate(
        id="test-tmpl", name="Test", adapter="echo",
        config={"model": "test"}, default_role="af:agent",
        soul_template="You are a test agent.", description="test",
    ))
    f.spawn("test-tmpl", "bot-1")
    return f


def test_chat_returns_agent_info(forge):
    from agent_forge.mcp_tools.chat import _chat
    result = _chat(forge, agent_name="bot-1", message="hello")
    assert result["agent_name"] == "bot-1"
    assert result["message_received"] == "hello"
    assert "reply" in result


def test_chat_nonexistent_agent(forge):
    from agent_forge.mcp_tools.chat import _chat
    result = _chat(forge, agent_name="ghost", message="hello")
    assert "error" in result


def test_chat_sleeping_agent_error(forge):
    from agent_forge.mcp_tools.chat import _chat
    forge.sleep("bot-1")
    result = _chat(forge, agent_name="bot-1", message="hello")
    assert "error" in result
    assert "sleeping" in result["error"].lower() or "not active" in result["error"].lower()
