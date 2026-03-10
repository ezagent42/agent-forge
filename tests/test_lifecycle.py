import pytest
from agent_forge.lifecycle import AgentLifecycle, InvalidTransition
from agent_forge.models import AgentStatus


def test_initial_state():
    lc = AgentLifecycle()
    assert lc.state == AgentStatus.CREATED


def test_spawn_transition():
    lc = AgentLifecycle()
    lc.spawn()
    assert lc.state == AgentStatus.ACTIVE


def test_sleep_transition():
    lc = AgentLifecycle()
    lc.spawn()
    lc.sleep()
    assert lc.state == AgentStatus.SLEEPING


def test_wake_transition():
    lc = AgentLifecycle()
    lc.spawn()
    lc.sleep()
    lc.wake()
    assert lc.state == AgentStatus.ACTIVE


def test_destroy_from_active():
    lc = AgentLifecycle()
    lc.spawn()
    lc.destroy()
    assert lc.state == AgentStatus.DESTROYED


def test_destroy_from_sleeping():
    lc = AgentLifecycle()
    lc.spawn()
    lc.sleep()
    lc.destroy()
    assert lc.state == AgentStatus.DESTROYED


def test_invalid_sleep_from_created():
    lc = AgentLifecycle()
    with pytest.raises(InvalidTransition):
        lc.sleep()


def test_invalid_spawn_from_active():
    lc = AgentLifecycle()
    lc.spawn()
    with pytest.raises(InvalidTransition):
        lc.spawn()


def test_invalid_transition_from_destroyed():
    lc = AgentLifecycle()
    lc.spawn()
    lc.destroy()
    with pytest.raises(InvalidTransition):
        lc.wake()


def test_transition_history():
    lc = AgentLifecycle()
    lc.spawn()
    lc.sleep()
    lc.wake()
    assert lc.history == [
        (AgentStatus.CREATED, AgentStatus.ACTIVE),
        (AgentStatus.ACTIVE, AgentStatus.SLEEPING),
        (AgentStatus.SLEEPING, AgentStatus.ACTIVE),
    ]
