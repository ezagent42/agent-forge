import pytest
from agent_forge.context_builder import ContextBuilder, SegmentConfig
from agent_forge.models import ContextMessage


def _msg(ref_id, content, author="@alice:r", thread_id=None, reply_to=None,
         channels=None, timestamp="2026-03-06T10:00:00Z"):
    return {
        "ref_id": ref_id, "content": content, "author": author,
        "thread_id": thread_id, "reply_to": reply_to,
        "channels": channels or [], "timestamp": timestamp,
    }


@pytest.fixture
def builder():
    return ContextBuilder(config=SegmentConfig(
        max_context_messages=10, max_context_tokens=8000, min_context_messages=3,
    ))


def test_thread_is_segment(builder):
    history = [
        _msg("r1", "Thread root", thread_id=None),
        _msg("r2", "Reply 1", thread_id="r1"),
        _msg("r3", "Reply 2", thread_id="r1"),
        _msg("r4", "@bot help", thread_id="r1"),
        _msg("r5", "Unrelated msg"),
    ]
    trigger = _msg("r4", "@bot help", thread_id="r1")
    segment = builder.build(trigger, history)
    ref_ids = [m.ref_id for m in segment]
    assert ref_ids == ["r1", "r2", "r3", "r4"]
    assert "r5" not in ref_ids


def test_reply_chain(builder):
    history = [
        _msg("r1", "Original question"),
        _msg("r2", "Follow up", reply_to="r1"),
        _msg("r3", "@bot answer this", reply_to="r2"),
        _msg("r4", "Noise"),
    ]
    trigger = _msg("r3", "@bot answer this", reply_to="r2")
    segment = builder.build(trigger, history)
    ref_ids = [m.ref_id for m in segment]
    assert "r1" in ref_ids
    assert "r2" in ref_ids
    assert "r3" in ref_ids


def test_channel_fallback(builder):
    history = [
        _msg("r1", "msg 1", channels=["code-review"]),
        _msg("r2", "msg 2", channels=["code-review"]),
        _msg("r3", "msg 3", channels=["general"]),
        _msg("r4", "@bot help", channels=["code-review"]),
    ]
    trigger = _msg("r4", "@bot help", channels=["code-review"])
    segment = builder.build(trigger, history)
    ref_ids = [m.ref_id for m in segment]
    assert "r1" in ref_ids
    assert "r2" in ref_ids
    assert "r3" not in ref_ids


def test_empty_history(builder):
    trigger = _msg("r1", "@bot help")
    segment = builder.build(trigger, [])
    assert len(segment) == 0
