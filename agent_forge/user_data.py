from __future__ import annotations
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib

_DEFAULT_CONFIG = """\
[adapter]
default = "claude"

[adapter.claude]
model = "claude-sonnet-4-6"
api_key_env = "ANTHROPIC_API_KEY"

[limits]
max_agents = 50
max_concurrent_per_agent = 3
default_idle_timeout = "1h"
"""


class UserDataManager:
    def __init__(self, base_dir: Path | None = None):
        self.base_dir = base_dir or Path.home() / ".agent-forge"

    @property
    def templates_dir(self) -> Path:
        return self.base_dir / "templates"

    @property
    def instances_dir(self) -> Path:
        return self.base_dir / "instances"

    @property
    def logs_dir(self) -> Path:
        return self.base_dir / "logs"

    @property
    def config_path(self) -> Path:
        return self.base_dir / "config.toml"

    def init(self) -> None:
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.templates_dir.mkdir(exist_ok=True)
        self.instances_dir.mkdir(exist_ok=True)
        self.logs_dir.mkdir(exist_ok=True)
        if not self.config_path.exists():
            self.config_path.write_text(_DEFAULT_CONFIG, encoding="utf-8")

    def load_config(self) -> dict:
        with open(self.config_path, "rb") as f:
            return tomllib.load(f)
