import pytest
from agent_forge.cooperation import CooperationEngine, PipelineStep


def test_pipeline_definition():
    pipeline = CooperationEngine.pipeline(
        name="code-review-pipeline",
        steps=[
            PipelineStep(role="coder", template="task-worker", trigger="task.assign"),
            PipelineStep(role="reviewer", template="code-reviewer", trigger="task.submit"),
            PipelineStep(role="tester", template="task-worker", trigger="review.approved"),
        ],
    )
    assert pipeline.name == "code-review-pipeline"
    assert len(pipeline.steps) == 3


def test_pipeline_next_step():
    pipeline = CooperationEngine.pipeline(
        name="test",
        steps=[
            PipelineStep(role="a", template="t1", trigger="start"),
            PipelineStep(role="b", template="t2", trigger="a.done"),
        ],
    )
    step = pipeline.next_step("a.done")
    assert step is not None
    assert step.role == "b"


def test_pipeline_no_next():
    pipeline = CooperationEngine.pipeline(
        name="test",
        steps=[PipelineStep(role="a", template="t1", trigger="start")],
    )
    step = pipeline.next_step("a.done")
    assert step is None


def test_ensemble_definition():
    ensemble = CooperationEngine.ensemble(
        name="review-ensemble",
        agents=["reviewer-1", "reviewer-2", "reviewer-3"],
        strategy="majority",
    )
    assert ensemble.name == "review-ensemble"
    assert len(ensemble.agents) == 3
    assert ensemble.strategy == "majority"
