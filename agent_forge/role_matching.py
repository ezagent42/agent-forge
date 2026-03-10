from __future__ import annotations
from dataclasses import dataclass


@dataclass
class StaffingRule:
    role_id: str
    prefer: str
    template: str
    auto_spawn: bool = False


class RoleMatcher:
    def __init__(self, rules: list[StaffingRule]):
        self._rules = {r.role_id: r for r in rules}

    def match(self, role_id: str) -> StaffingRule | None:
        return self._rules.get(role_id)

    def auto_spawn_roles(self) -> list[StaffingRule]:
        return [r for r in self._rules.values() if r.auto_spawn]
