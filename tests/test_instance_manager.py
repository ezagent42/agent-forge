import pytest
from agent_forge.instance_manager import InstanceManager
from agent_forge.template_registry import TemplateRegistry
from agent_forge.models import AgentStatus, AgentTemplate


@pytest.fixture
def setup(tmp_path):
    registry = TemplateRegistry(templates_dir=tmp_path)
    registry.register(AgentTemplate(
        id="test-tmpl", name="Test", adapter="echo",
        config={"model": "test"}, default_role="af:agent",
        soul_template="test", description="test template",
    ))
    manager = InstanceManager(registry=registry, data_dir=tmp_path / "agents")
    return manager, registry


def test_spawn_creates_instance(setup):
    mgr, _ = setup
    inst = mgr.spawn(template_id="test-tmpl", agent_name="bot-1", rooms=["room-a"])
    assert inst.agent_name == "bot-1"
    assert inst.template_id == "test-tmpl"
    assert inst.status == AgentStatus.ACTIVE
    assert "room-a" in inst.rooms


def test_spawn_duplicate_raises(setup):
    mgr, _ = setup
    mgr.spawn(template_id="test-tmpl", agent_name="bot-1")
    with pytest.raises(ValueError, match="already exists"):
        mgr.spawn(template_id="test-tmpl", agent_name="bot-1")


def test_spawn_invalid_template_raises(setup):
    mgr, _ = setup
    with pytest.raises(KeyError, match="not found"):
        mgr.spawn(template_id="nonexistent", agent_name="bot-x")


def test_destroy_instance(setup):
    mgr, _ = setup
    mgr.spawn(template_id="test-tmpl", agent_name="bot-1")
    mgr.destroy("bot-1")
    inst = mgr.get("bot-1")
    assert inst.status == AgentStatus.DESTROYED


def test_list_instances(setup):
    mgr, _ = setup
    mgr.spawn(template_id="test-tmpl", agent_name="bot-1")
    mgr.spawn(template_id="test-tmpl", agent_name="bot-2")
    all_inst = mgr.list()
    assert len(all_inst) == 2


def test_list_by_status(setup):
    mgr, _ = setup
    mgr.spawn(template_id="test-tmpl", agent_name="bot-1")
    mgr.spawn(template_id="test-tmpl", agent_name="bot-2")
    mgr.sleep("bot-2")
    active = mgr.list(status=AgentStatus.ACTIVE)
    assert len(active) == 1
    assert active[0].agent_name == "bot-1"


def test_sleep_and_wake(setup):
    mgr, _ = setup
    mgr.spawn(template_id="test-tmpl", agent_name="bot-1")
    mgr.sleep("bot-1")
    assert mgr.get("bot-1").status == AgentStatus.SLEEPING
    mgr.wake("bot-1")
    assert mgr.get("bot-1").status == AgentStatus.ACTIVE


def test_get_nonexistent_raises(setup):
    mgr, _ = setup
    with pytest.raises(KeyError, match="not found"):
        mgr.get("ghost")
