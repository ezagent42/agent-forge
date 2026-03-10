from __future__ import annotations
from pathlib import Path
from agent_forge.template_registry import TemplateRegistry
from agent_forge.instance_manager import InstanceManager
from agent_forge.resource_guard import ResourceGuard
from agent_forge.context_builder import ContextBuilder, SegmentConfig
from agent_forge.cooperation import CooperationEngine
from agent_forge.role_matching import RoleMatcher, StaffingRule
from agent_forge.models import AgentInstance, AgentStatus


class AgentForge:
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.templates = TemplateRegistry(templates_dir=base_dir / "templates")
        self.instances = InstanceManager(
            registry=self.templates, data_dir=base_dir / "agents"
        )
        self.guard = ResourceGuard()
        self.context = ContextBuilder()
        self.cooperation = CooperationEngine()
        self._role_matcher: RoleMatcher | None = None

    def init(self) -> None:
        self.templates.load_from_dir()

    def spawn(
        self, template_id: str, agent_name: str, rooms: list[str] | None = None
    ) -> AgentInstance:
        self.guard.check_agent_limit(len(self.instances.list()))
        return self.instances.spawn(template_id, agent_name, rooms)

    def destroy(self, agent_name: str) -> None:
        self.instances.destroy(agent_name)

    def sleep(self, agent_name: str) -> None:
        self.instances.sleep(agent_name)

    def wake(self, agent_name: str) -> None:
        self.instances.wake(agent_name)

    def list_agents(self, status: AgentStatus | None = None) -> list[AgentInstance]:
        return self.instances.list(status)

    def export_agent(self, agent_name: str, output_dir: Path | None = None) -> Path:
        target = output_dir or self.base_dir
        return self.instances.export_agent(agent_name, output_dir=target)

    def import_agent(self, file_path: Path, new_name: str | None = None) -> AgentInstance:
        self.guard.check_agent_limit(len(self.instances.list()))
        return self.instances.import_agent(file_path, new_name=new_name)

    def set_role_matcher(self, rules: list[StaffingRule]) -> None:
        self._role_matcher = RoleMatcher(rules)
