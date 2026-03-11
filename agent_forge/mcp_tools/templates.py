from __future__ import annotations
from pathlib import Path
from typing import Any

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib

from agent_forge.core import AgentForge
from agent_forge.models import AgentTemplate


def _template_to_dict(t: AgentTemplate) -> dict[str, Any]:
    return {
        "id": t.id,
        "name": t.name,
        "adapter": t.adapter,
        "default_role": t.default_role,
        "description": t.description,
    }


def _list_templates(forge: AgentForge) -> list[dict[str, Any]]:
    return [_template_to_dict(t) for t in forge.templates.list()]


def _register_template(
    forge: AgentForge,
    template_def: str,
    user_templates_dir: Path,
) -> dict[str, Any]:
    try:
        data = tomllib.loads(template_def)
        template = AgentTemplate(
            id=data["id"],
            name=data["name"],
            adapter=data["adapter"],
            config=data.get("config", {}),
            default_role=data.get("default_role", "af:agent"),
            soul_template=data.get("soul_template", ""),
            description=data.get("description", ""),
        )
        forge.templates.register(template)
        out_path = user_templates_dir / f"{template.id}.toml"
        out_path.write_text(template_def, encoding="utf-8")
        return _template_to_dict(template)
    except (KeyError, ValueError) as e:
        return {"error": str(e)}


def _unregister_template(
    forge: AgentForge, template_id: str
) -> dict[str, Any]:
    try:
        forge.templates.unregister(template_id)
        return {"status": "removed", "template_id": template_id}
    except KeyError as e:
        return {"error": str(e)}


def register_template_tools(server, forge: AgentForge, user_templates_dir: Path):
    """Register all 3 template management tools on the MCP server."""

    @server.tool()
    async def list_templates() -> str:
        """List all available agent templates (built-in + user-defined)."""
        import json
        return json.dumps(_list_templates(forge), ensure_ascii=False)

    @server.tool()
    async def register_template(template_def: str) -> str:
        """Register a new agent template from a TOML definition string.

        Args:
            template_def: Full TOML template definition with id, name, adapter, config, soul_template, description
        """
        import json
        return json.dumps(
            _register_template(forge, template_def, user_templates_dir),
            ensure_ascii=False,
        )

    @server.tool()
    async def unregister_template(template_id: str) -> str:
        """Remove a registered agent template.

        Args:
            template_id: ID of the template to remove
        """
        import json
        return json.dumps(
            _unregister_template(forge, template_id), ensure_ascii=False
        )
