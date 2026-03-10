from __future__ import annotations
from datetime import datetime, timezone
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib

from agent_forge.models import AgentInstance, AgentStatus, AgentTemplate
from agent_forge.lifecycle import AgentLifecycle
from agent_forge.template_registry import TemplateRegistry


def _toml_value(v: object) -> str:
    """Format a Python value as a TOML value."""
    if isinstance(v, str):
        if "\n" in v:
            return f'"""\n{v}"""'
        return f'"{v}"'
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, int):
        return str(v)
    if isinstance(v, float):
        return str(v)
    if isinstance(v, list):
        items = ", ".join(_toml_value(i) for i in v)
        return f"[{items}]"
    return f'"{v}"'


def _to_toml(data: dict, prefix: str = "") -> str:
    """Serialize a nested dict to TOML string (simple subset)."""
    lines: list[str] = []
    scalars: dict = {}
    tables: dict = {}

    for k, v in data.items():
        if isinstance(v, dict):
            tables[k] = v
        else:
            scalars[k] = v

    if prefix:
        lines.append(f"[{prefix}]")

    for k, v in scalars.items():
        lines.append(f"{k} = {_toml_value(v)}")

    if scalars and tables:
        lines.append("")

    for k, v in tables.items():
        full_key = f"{prefix}.{k}" if prefix else k
        lines.append(_to_toml(v, prefix=full_key))

    return "\n".join(lines)


class InstanceManager:
    def __init__(self, registry: TemplateRegistry, data_dir: Path | None = None):
        self._registry = registry
        self._data_dir = data_dir
        self._instances: dict[str, AgentInstance] = {}
        self._lifecycles: dict[str, AgentLifecycle] = {}

    def spawn(
        self, template_id: str, agent_name: str, rooms: list[str] | None = None
    ) -> AgentInstance:
        if agent_name in self._instances:
            raise ValueError(f"Agent '{agent_name}' already exists")
        template = self._registry.get(template_id)
        now = datetime.now(timezone.utc).isoformat()
        instance = AgentInstance(
            agent_name=agent_name,
            template_id=template_id,
            status=AgentStatus.ACTIVE,
            rooms=rooms or [],
            config=dict(template.config),
            limits={"max_concurrent": 3, "api_budget_daily": 500},
            lifecycle={
                "auto_start": True,
                "idle_timeout": "1h",
                "auto_wake_on_mention": True,
            },
            created_at=now,
            last_active_at=now,
        )
        lc = AgentLifecycle()
        lc.spawn()
        self._instances[agent_name] = instance
        self._lifecycles[agent_name] = lc
        return instance

    def destroy(self, agent_name: str) -> None:
        inst = self._get_or_raise(agent_name)
        self._lifecycles[agent_name].destroy()
        inst.status = AgentStatus.DESTROYED

    def sleep(self, agent_name: str) -> None:
        inst = self._get_or_raise(agent_name)
        self._lifecycles[agent_name].sleep()
        inst.status = AgentStatus.SLEEPING

    def wake(self, agent_name: str) -> None:
        inst = self._get_or_raise(agent_name)
        self._lifecycles[agent_name].wake()
        inst.status = AgentStatus.ACTIVE
        inst.last_active_at = datetime.now(timezone.utc).isoformat()

    def get(self, agent_name: str) -> AgentInstance:
        return self._get_or_raise(agent_name)

    def list(self, status: AgentStatus | None = None) -> list[AgentInstance]:
        instances = list(self._instances.values())
        if status is not None:
            instances = [i for i in instances if i.status == status]
        return instances

    def _get_or_raise(self, agent_name: str) -> AgentInstance:
        if agent_name not in self._instances:
            raise KeyError(f"Agent '{agent_name}' not found")
        return self._instances[agent_name]

    def export_agent(self, agent_name: str, output_dir: Path) -> Path:
        """Export an agent instance as a self-contained .agent.toml file."""
        inst = self._get_or_raise(agent_name)
        template = self._registry.get(inst.template_id)
        now = datetime.now(timezone.utc).isoformat()

        export_data = {
            "export": {"version": "1.0", "exported_at": now},
            "template": {
                "id": template.id,
                "name": template.name,
                "adapter": template.adapter,
                "default_role": template.default_role,
                "description": template.description,
                "soul_template": template.soul_template,
                "config": dict(template.config),
            },
            "agent": {
                "name": inst.agent_name,
                "template_id": inst.template_id,
                "config": dict(inst.config),
                "limits": dict(inst.limits),
                "lifecycle": dict(inst.lifecycle),
                "rooms": {"list": list(inst.rooms)},
            },
            "soul": {"content": template.soul_template},
        }

        output_path = output_dir / f"{agent_name}.agent.toml"
        output_path.write_text(_to_toml(export_data), encoding="utf-8")
        return output_path

    def import_agent(
        self, file_path: Path, new_name: str | None = None
    ) -> AgentInstance:
        """Import an agent from a .agent.toml file."""
        with open(file_path, "rb") as f:
            data = tomllib.load(f)

        agent_data = data["agent"]
        template_data = data["template"]
        agent_name = new_name or agent_data["name"]

        if agent_name in self._instances:
            raise ValueError(f"Agent '{agent_name}' already exists")

        # Auto-register template if not present
        template_id = agent_data["template_id"]
        try:
            self._registry.get(template_id)
        except KeyError:
            self._registry.register(AgentTemplate(
                id=template_data["id"],
                name=template_data["name"],
                adapter=template_data["adapter"],
                config=template_data.get("config", {}),
                default_role=template_data.get("default_role", "af:agent"),
                soul_template=template_data.get("soul_template", ""),
                description=template_data.get("description", ""),
            ))

        now = datetime.now(timezone.utc).isoformat()
        rooms_data = agent_data.get("rooms", {})
        rooms = rooms_data.get("list", []) if isinstance(rooms_data, dict) else []

        instance = AgentInstance(
            agent_name=agent_name,
            template_id=template_id,
            status=AgentStatus.ACTIVE,
            rooms=rooms,
            config=dict(agent_data.get("config", {})),
            limits=dict(agent_data.get("limits", {})),
            lifecycle=dict(agent_data.get("lifecycle", {})),
            created_at=now,
            last_active_at=now,
        )
        lc = AgentLifecycle()
        lc.spawn()
        self._instances[agent_name] = instance
        self._lifecycles[agent_name] = lc
        return instance
