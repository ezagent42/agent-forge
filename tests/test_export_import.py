import pytest
from pathlib import Path
from agent_forge.instance_manager import InstanceManager
from agent_forge.template_registry import TemplateRegistry
from agent_forge.models import AgentStatus, AgentTemplate

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib


@pytest.fixture
def forge_env(tmp_path):
    """Set up AgentForge environment with template and spawned agent."""
    templates_dir = tmp_path / "templates"
    templates_dir.mkdir()
    agents_dir = tmp_path / "agents"
    agents_dir.mkdir()

    registry = TemplateRegistry(templates_dir=templates_dir)
    registry.register(AgentTemplate(
        id="test-tmpl", name="Test Template", adapter="claude-code",
        config={"model": "sonnet", "allowed_tools": ["Read", "Write"], "max_tokens": 4096},
        default_role="af:agent",
        soul_template="# Test Agent\n\nYou are a test agent.",
        description="A test template",
    ))
    manager = InstanceManager(registry=registry, data_dir=agents_dir)
    manager.spawn(template_id="test-tmpl", agent_name="test-bot", rooms=["room-a"])
    return manager, registry, tmp_path


def test_export_creates_file(forge_env):
    mgr, _, base = forge_env
    out = mgr.export_agent("test-bot", output_dir=base)
    assert out.exists()
    assert out.name == "test-bot.agent.toml"


def test_export_file_contains_all_sections(forge_env):
    mgr, _, base = forge_env
    out = mgr.export_agent("test-bot", output_dir=base)
    with open(out, "rb") as f:
        data = tomllib.load(f)
    assert "export" in data
    assert data["export"]["version"] == "1.0"
    assert "template" in data
    assert data["template"]["id"] == "test-tmpl"
    assert "agent" in data
    assert data["agent"]["name"] == "test-bot"
    assert "soul" in data
    assert "test agent" in data["soul"]["content"].lower()


def test_export_nonexistent_raises(forge_env):
    mgr, _, base = forge_env
    with pytest.raises(KeyError, match="not found"):
        mgr.export_agent("ghost", output_dir=base)


def test_export_preserves_template_config(forge_env):
    mgr, _, base = forge_env
    out = mgr.export_agent("test-bot", output_dir=base)
    with open(out, "rb") as f:
        data = tomllib.load(f)
    assert data["template"]["config"]["model"] == "sonnet"
    assert data["template"]["config"]["allowed_tools"] == ["Read", "Write"]


def test_import_creates_agent(forge_env):
    mgr, _, base = forge_env
    out = mgr.export_agent("test-bot", output_dir=base)
    mgr.destroy("test-bot")
    imported = mgr.import_agent(out, new_name="test-bot-2")
    assert imported.agent_name == "test-bot-2"
    assert imported.status == AgentStatus.ACTIVE
    assert imported.template_id == "test-tmpl"


def test_import_uses_original_name_by_default(forge_env):
    mgr, _, base = forge_env
    out = mgr.export_agent("test-bot", output_dir=base)
    mgr.destroy("test-bot")
    del mgr._instances["test-bot"]
    del mgr._lifecycles["test-bot"]
    imported = mgr.import_agent(out)
    assert imported.agent_name == "test-bot"


def test_import_name_conflict_raises(forge_env):
    mgr, _, base = forge_env
    out = mgr.export_agent("test-bot", output_dir=base)
    with pytest.raises(ValueError, match="already exists"):
        mgr.import_agent(out)


def test_import_auto_registers_template(tmp_path):
    templates_dir = tmp_path / "templates"
    templates_dir.mkdir()
    agents_dir = tmp_path / "agents"
    agents_dir.mkdir()
    registry = TemplateRegistry(templates_dir=templates_dir)
    manager = InstanceManager(registry=registry, data_dir=agents_dir)

    toml_content = '''
[export]
version = "1.0"
exported_at = "2026-03-10T00:00:00Z"

[template]
id = "imported-tmpl"
name = "Imported Template"
adapter = "claude-code"
default_role = "af:agent"
description = "An imported template"
soul_template = "# Imported Agent"

[template.config]
model = "sonnet"
allowed_tools = ["Read"]
max_tokens = 4096

[agent]
name = "imported-bot"
template_id = "imported-tmpl"

[agent.config]
model = "sonnet"
allowed_tools = ["Read"]
max_tokens = 4096

[agent.limits]
max_concurrent = 3
api_budget_daily = 500

[agent.lifecycle]
auto_start = true
idle_timeout = "1h"
auto_wake_on_mention = true

[agent.rooms]
list = ["room-x"]

[soul]
content = "# Imported Agent"
'''
    agent_file = tmp_path / "imported-bot.agent.toml"
    agent_file.write_text(toml_content, encoding="utf-8")
    imported = manager.import_agent(agent_file)
    assert imported.agent_name == "imported-bot"
    assert imported.status == AgentStatus.ACTIVE
    tmpl = registry.get("imported-tmpl")
    assert tmpl.name == "Imported Template"


def test_import_skips_existing_template(forge_env):
    mgr, registry, base = forge_env
    out = mgr.export_agent("test-bot", output_dir=base)
    mgr.destroy("test-bot")
    del mgr._instances["test-bot"]
    del mgr._lifecycles["test-bot"]
    imported = mgr.import_agent(out)
    assert imported.agent_name == "test-bot"
    assert registry.get("test-tmpl").name == "Test Template"


def test_import_sets_status_active(tmp_path):
    templates_dir = tmp_path / "templates"
    templates_dir.mkdir()
    agents_dir = tmp_path / "agents"
    agents_dir.mkdir()
    registry = TemplateRegistry(templates_dir=templates_dir)
    manager = InstanceManager(registry=registry, data_dir=agents_dir)

    toml_content = '''
[export]
version = "1.0"
exported_at = "2026-03-10T00:00:00Z"

[template]
id = "tmpl-x"
name = "X"
adapter = "claude-code"
default_role = "af:agent"
description = "x"
soul_template = "# X"

[template.config]
model = "sonnet"
allowed_tools = ["Read"]
max_tokens = 4096

[agent]
name = "sleeping-bot"
template_id = "tmpl-x"

[agent.config]
model = "sonnet"
allowed_tools = ["Read"]
max_tokens = 4096

[agent.limits]
max_concurrent = 3
api_budget_daily = 500

[agent.lifecycle]
auto_start = true
idle_timeout = "1h"
auto_wake_on_mention = true

[agent.rooms]
list = []

[soul]
content = "# X"
'''
    agent_file = tmp_path / "sleeping-bot.agent.toml"
    agent_file.write_text(toml_content, encoding="utf-8")
    imported = manager.import_agent(agent_file)
    assert imported.status == AgentStatus.ACTIVE
