# src/template_registry.py
from __future__ import annotations
from pathlib import Path
from agent_forge.models import AgentTemplate

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib


class TemplateRegistry:
    def __init__(self, templates_dir: Path | None = None):
        self._templates: dict[str, AgentTemplate] = {}
        self._templates_dir = templates_dir

    def register(self, template: AgentTemplate) -> None:
        if template.id in self._templates:
            raise ValueError(f"Template '{template.id}' already registered")
        self._templates[template.id] = template

    def unregister(self, template_id: str) -> None:
        if template_id not in self._templates:
            raise KeyError(f"Template '{template_id}' not found")
        del self._templates[template_id]

    def get(self, template_id: str) -> AgentTemplate:
        if template_id not in self._templates:
            raise KeyError(f"Template '{template_id}' not found")
        return self._templates[template_id]

    def list(self) -> list[AgentTemplate]:
        return list(self._templates.values())

    def load_from_dir(self) -> None:
        if self._templates_dir is None:
            return
        for path in self._templates_dir.glob("*.toml"):
            with open(path, "rb") as f:
                data = tomllib.load(f)
            template = AgentTemplate(
                id=data["id"],
                name=data["name"],
                adapter=data["adapter"],
                config=data.get("config", {}),
                default_role=data.get("default_role", "af:agent"),
                soul_template=data.get("soul_template", ""),
                description=data.get("description", ""),
            )
            self._templates[template.id] = template
