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
        id="code-reviewer", name="Code Reviewer", adapter="claude",
        config={"model": "sonnet"}, default_role="af:agent",
        soul_template="You review code.", description="Reviews PRs",
    ))
    return f


@pytest.fixture
def user_templates_dir(tmp_path):
    d = tmp_path / "user_templates"
    d.mkdir()
    return d


def test_list_templates(forge):
    from agent_forge.mcp_tools.templates import _list_templates
    result = _list_templates(forge)
    assert len(result) == 1
    assert result[0]["id"] == "code-reviewer"


def test_register_template(forge, user_templates_dir):
    from agent_forge.mcp_tools.templates import _register_template
    toml_str = """
id = "my-bot"
name = "My Bot"
adapter = "claude"
default_role = "af:agent"
soul_template = "You are my bot."
description = "Custom bot"

[config]
model = "sonnet"
"""
    result = _register_template(forge, toml_str, user_templates_dir)
    assert result["id"] == "my-bot"
    assert (user_templates_dir / "my-bot.toml").exists()


def test_register_duplicate_template(forge, user_templates_dir):
    from agent_forge.mcp_tools.templates import _register_template
    toml_str = """
id = "code-reviewer"
name = "Duplicate"
adapter = "claude"
default_role = "af:agent"
soul_template = "dup"
description = "dup"
"""
    result = _register_template(forge, toml_str, user_templates_dir)
    assert "error" in result


def test_unregister_template(forge):
    from agent_forge.mcp_tools.templates import _unregister_template
    result = _unregister_template(forge, "code-reviewer")
    assert result["status"] == "removed"


def test_unregister_nonexistent(forge):
    from agent_forge.mcp_tools.templates import _unregister_template
    result = _unregister_template(forge, "ghost")
    assert "error" in result
