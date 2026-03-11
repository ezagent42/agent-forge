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
        id="reviewer", name="Reviewer", adapter="echo",
        config={}, default_role="af:agent",
        soul_template="Review code.", description="reviewer",
    ))
    f.templates.register(AgentTemplate(
        id="worker", name="Worker", adapter="echo",
        config={}, default_role="af:agent",
        soul_template="Do tasks.", description="worker",
    ))
    return f


def test_run_pipeline_creates_agents(forge):
    from agent_forge.mcp_tools.cooperation import _run_pipeline
    steps = [
        {"role": "reviewer", "template": "reviewer", "trigger": "start"},
        {"role": "worker", "template": "worker", "trigger": "review_done"},
    ]
    result = _run_pipeline(forge, steps=steps, input_text="Review this code")
    assert result["pipeline_name"] is not None
    assert len(result["steps"]) == 2
    assert result["status"] == "created"


def test_run_ensemble_creates_agents(forge):
    from agent_forge.mcp_tools.cooperation import _run_ensemble
    result = _run_ensemble(
        forge,
        agents=[
            {"template": "reviewer", "name": "r1"},
            {"template": "worker", "name": "w1"},
        ],
        input_text="Analyze this",
        strategy="majority",
    )
    assert len(result["agents"]) == 2
    assert result["strategy"] == "majority"
    assert result["status"] == "created"


def test_run_pipeline_invalid_template(forge):
    from agent_forge.mcp_tools.cooperation import _run_pipeline
    steps = [{"role": "x", "template": "nonexistent", "trigger": "start"}]
    result = _run_pipeline(forge, steps=steps, input_text="test")
    assert "error" in result
