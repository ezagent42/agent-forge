import pytest
from pathlib import Path
from agent_forge.mcp_tools.lifecycle import register_lifecycle_tools
from agent_forge.core import AgentForge
from agent_forge.models import AgentTemplate


@pytest.fixture
def forge(tmp_path):
    builtin_dir = tmp_path / "builtin" / "templates"
    builtin_dir.mkdir(parents=True)
    user_dir = tmp_path / "user"
    user_dir.mkdir()
    (user_dir / "templates").mkdir()
    (user_dir / "instances").mkdir()

    f = AgentForge(base_dir=tmp_path / "builtin")
    f.templates.register(AgentTemplate(
        id="test-tmpl", name="Test", adapter="echo",
        config={"model": "test"}, default_role="af:agent",
        soul_template="You are a test agent.", description="test",
    ))
    return f


def test_spawn_agent_tool(forge):
    from agent_forge.mcp_tools.lifecycle import _spawn_agent
    result = _spawn_agent(forge, template_id="test-tmpl", agent_name="bot-1")
    assert result["status"] == "active"
    assert result["agent_name"] == "bot-1"


def test_list_agents_tool(forge):
    from agent_forge.mcp_tools.lifecycle import _spawn_agent, _list_agents
    _spawn_agent(forge, template_id="test-tmpl", agent_name="bot-1")
    result = _list_agents(forge)
    assert len(result) == 1
    assert result[0]["agent_name"] == "bot-1"


def test_get_agent_tool(forge):
    from agent_forge.mcp_tools.lifecycle import _spawn_agent, _get_agent
    _spawn_agent(forge, template_id="test-tmpl", agent_name="bot-1")
    result = _get_agent(forge, agent_name="bot-1")
    assert result["agent_name"] == "bot-1"
    assert result["template_id"] == "test-tmpl"


def test_sleep_agent_tool(forge):
    from agent_forge.mcp_tools.lifecycle import _spawn_agent, _sleep_agent
    _spawn_agent(forge, template_id="test-tmpl", agent_name="bot-1")
    result = _sleep_agent(forge, agent_name="bot-1")
    assert result["status"] == "sleeping"


def test_wake_agent_tool(forge):
    from agent_forge.mcp_tools.lifecycle import _spawn_agent, _sleep_agent, _wake_agent
    _spawn_agent(forge, template_id="test-tmpl", agent_name="bot-1")
    _sleep_agent(forge, agent_name="bot-1")
    result = _wake_agent(forge, agent_name="bot-1")
    assert result["status"] == "active"


def test_destroy_agent_tool(forge):
    from agent_forge.mcp_tools.lifecycle import _spawn_agent, _destroy_agent
    _spawn_agent(forge, template_id="test-tmpl", agent_name="bot-1")
    result = _destroy_agent(forge, agent_name="bot-1")
    assert result["status"] == "destroyed"


def test_spawn_nonexistent_template(forge):
    from agent_forge.mcp_tools.lifecycle import _spawn_agent
    result = _spawn_agent(forge, template_id="nope", agent_name="bot-x")
    assert "error" in result


def test_get_nonexistent_agent(forge):
    from agent_forge.mcp_tools.lifecycle import _get_agent
    result = _get_agent(forge, agent_name="ghost")
    assert "error" in result
