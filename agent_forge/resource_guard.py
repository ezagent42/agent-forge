from __future__ import annotations


class ResourceGuard:
    class LimitExceeded(Exception):
        def __init__(self, code: str, message: str):
            self.code = code
            super().__init__(f"{code}: {message}")

    def __init__(self, max_agents: int = 50, max_concurrent_per_agent: int = 3, default_idle_timeout: str = "1h"):
        self.max_agents = max_agents
        self.max_concurrent_per_agent = max_concurrent_per_agent
        self.default_idle_timeout = default_idle_timeout

    def check_agent_limit(self, current_count: int) -> None:
        if current_count >= self.max_agents:
            raise self.LimitExceeded("MAX_AGENTS_REACHED", f"Agent limit {self.max_agents} reached")

    def check_concurrent(self, agent_name: str, current_concurrent: int, max_concurrent: int) -> None:
        if current_concurrent >= max_concurrent:
            raise self.LimitExceeded("AGENT_BUSY", f"Agent '{agent_name}' concurrent limit {max_concurrent} reached")

    def check_budget(self, agent_name: str, used_today: int, daily_limit: int) -> None:
        if used_today >= daily_limit:
            raise self.LimitExceeded("BUDGET_EXHAUSTED", f"Agent '{agent_name}' daily budget {daily_limit} exhausted")

    def check_sandbox(self, target_path: str, allowed_paths: list[dict[str, str]]) -> None:
        for entry in allowed_paths:
            if target_path.startswith(entry["path"]):
                return
        raise self.LimitExceeded("SANDBOX_VIOLATION", f"Path '{target_path}' not in allowed sandbox")
