import pytest
from agent_forge.role_matching import RoleMatcher, StaffingRule


def test_match_agent_preferred():
    rules = [
        StaffingRule(role_id="cv:mentor", prefer="agent_preferred", template="code-assistant", auto_spawn=True),
    ]
    matcher = RoleMatcher(rules)
    result = matcher.match("cv:mentor")
    assert result is not None
    assert result.template == "code-assistant"
    assert result.auto_spawn is True


def test_no_match():
    matcher = RoleMatcher([])
    result = matcher.match("cv:mentor")
    assert result is None


def test_auto_spawn_roles():
    rules = [
        StaffingRule(role_id="cv:mentor", prefer="agent", template="t1", auto_spawn=True),
        StaffingRule(role_id="ta:worker", prefer="human_preferred", template="t2", auto_spawn=False),
        StaffingRule(role_id="ta:reviewer", prefer="agent_preferred", template="t3", auto_spawn=True),
    ]
    matcher = RoleMatcher(rules)
    auto = matcher.auto_spawn_roles()
    assert len(auto) == 2
    role_ids = {r.role_id for r in auto}
    assert role_ids == {"cv:mentor", "ta:reviewer"}
