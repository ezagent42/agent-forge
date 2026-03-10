from __future__ import annotations
from agent_forge.models import AgentStatus


class InvalidTransition(Exception):
    pass


_TRANSITIONS: dict[tuple[AgentStatus, str], AgentStatus] = {
    (AgentStatus.CREATED, "spawn"): AgentStatus.ACTIVE,
    (AgentStatus.ACTIVE, "sleep"): AgentStatus.SLEEPING,
    (AgentStatus.SLEEPING, "wake"): AgentStatus.ACTIVE,
    (AgentStatus.ACTIVE, "destroy"): AgentStatus.DESTROYED,
    (AgentStatus.SLEEPING, "destroy"): AgentStatus.DESTROYED,
}


class AgentLifecycle:
    def __init__(self, initial: AgentStatus = AgentStatus.CREATED):
        self._state = initial
        self._history: list[tuple[AgentStatus, AgentStatus]] = []

    @property
    def state(self) -> AgentStatus:
        return self._state

    @property
    def history(self) -> list[tuple[AgentStatus, AgentStatus]]:
        return list(self._history)

    def _transition(self, action: str) -> None:
        key = (self._state, action)
        if key not in _TRANSITIONS:
            raise InvalidTransition(
                f"Cannot '{action}' from state {self._state.value}"
            )
        old = self._state
        self._state = _TRANSITIONS[key]
        self._history.append((old, self._state))

    def spawn(self) -> None:
        self._transition("spawn")

    def sleep(self) -> None:
        self._transition("sleep")

    def wake(self) -> None:
        self._transition("wake")

    def destroy(self) -> None:
        self._transition("destroy")
