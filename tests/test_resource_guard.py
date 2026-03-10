import pytest
from agent_forge.resource_guard import ResourceGuard


@pytest.fixture
def guard():
    return ResourceGuard(
        max_agents=3,
        max_concurrent_per_agent=2,
        default_idle_timeout="1h",
    )


def test_check_agent_limit_ok(guard):
    guard.check_agent_limit(current_count=2)


def test_check_agent_limit_exceeded(guard):
    with pytest.raises(ResourceGuard.LimitExceeded, match="MAX_AGENTS_REACHED"):
        guard.check_agent_limit(current_count=3)


def test_check_concurrent_ok(guard):
    guard.check_concurrent("bot-1", current_concurrent=1, max_concurrent=2)


def test_check_concurrent_exceeded(guard):
    with pytest.raises(ResourceGuard.LimitExceeded, match="AGENT_BUSY"):
        guard.check_concurrent("bot-1", current_concurrent=2, max_concurrent=2)


def test_check_budget_ok(guard):
    guard.check_budget("bot-1", used_today=499, daily_limit=500)


def test_check_budget_exceeded(guard):
    with pytest.raises(ResourceGuard.LimitExceeded, match="BUDGET_EXHAUSTED"):
        guard.check_budget("bot-1", used_today=500, daily_limit=500)


def test_check_sandbox_ok(guard):
    allowed = [{"path": "/projects/myapp", "access": "read-write"}]
    guard.check_sandbox("/projects/myapp/src/main.py", allowed)


def test_check_sandbox_violation(guard):
    allowed = [{"path": "/projects/myapp", "access": "read-only"}]
    with pytest.raises(ResourceGuard.LimitExceeded, match="SANDBOX_VIOLATION"):
        guard.check_sandbox("/etc/passwd", allowed)
