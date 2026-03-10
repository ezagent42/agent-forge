# tests/test_template_registry.py
import pytest
from pathlib import Path
from agent_forge.template_registry import TemplateRegistry
from agent_forge.models import AgentTemplate


@pytest.fixture
def registry(tmp_path):
    return TemplateRegistry(templates_dir=tmp_path)


def test_register_and_get(registry):
    t = AgentTemplate(
        id="code-reviewer", name="Code Reviewer", adapter="claude-code",
        config={"model": "sonnet"}, default_role="af:agent",
        soul_template="You review code.", description="Code reviewer agent",
    )
    registry.register(t)
    got = registry.get("code-reviewer")
    assert got.id == "code-reviewer"
    assert got.adapter == "claude-code"


def test_get_nonexistent(registry):
    with pytest.raises(KeyError, match="Template 'nonexistent' not found"):
        registry.get("nonexistent")


def test_list_templates(registry):
    t1 = AgentTemplate(id="a", name="A", adapter="x", config={},
                        default_role="af:agent", soul_template="", description="")
    t2 = AgentTemplate(id="b", name="B", adapter="y", config={},
                        default_role="af:agent", soul_template="", description="")
    registry.register(t1)
    registry.register(t2)
    templates = registry.list()
    assert len(templates) == 2
    ids = {t.id for t in templates}
    assert ids == {"a", "b"}


def test_unregister(registry):
    t = AgentTemplate(id="x", name="X", adapter="z", config={},
                       default_role="af:agent", soul_template="", description="")
    registry.register(t)
    registry.unregister("x")
    with pytest.raises(KeyError):
        registry.get("x")


def test_load_from_toml(tmp_path):
    toml_content = '''
id = "code-reviewer"
name = "Code Reviewer"
adapter = "claude-code"
default_role = "af:agent"
soul_template = "You are a code reviewer."
description = "Reviews code."

[config]
model = "sonnet"
allowed_tools = ["Read", "Search"]
max_tokens = 4096
'''
    (tmp_path / "code-reviewer.toml").write_text(toml_content)
    registry = TemplateRegistry(templates_dir=tmp_path)
    registry.load_from_dir()
    t = registry.get("code-reviewer")
    assert t.adapter == "claude-code"
    assert t.config["model"] == "sonnet"


def test_duplicate_register_raises(registry):
    t = AgentTemplate(id="dup", name="Dup", adapter="x", config={},
                       default_role="af:agent", soul_template="", description="")
    registry.register(t)
    with pytest.raises(ValueError, match="already registered"):
        registry.register(t)
