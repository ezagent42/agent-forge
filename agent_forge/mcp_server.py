"""agent-forge MCP Server — stdio mode entry point.

Usage:
    python -m agent_forge.mcp_server

Configuration in Claude Code (~/.claude/mcp_servers.json):
    {
      "agent-forge": {
        "command": "python",
        "args": ["-m", "agent_forge.mcp_server"]
      }
    }
"""
from __future__ import annotations
from pathlib import Path
from mcp.server.fastmcp import FastMCP

from agent_forge.core import AgentForge
from agent_forge.user_data import UserDataManager
from agent_forge.mcp_tools.lifecycle import register_lifecycle_tools
from agent_forge.mcp_tools.templates import register_template_tools
from agent_forge.mcp_tools.chat import register_chat_tools
from agent_forge.mcp_tools.cooperation import register_cooperation_tools


def create_server(
    builtin_templates_dir: Path | None = None,
    user_data_dir: Path | None = None,
) -> tuple[FastMCP, AgentForge]:
    # Resolve paths
    pkg_dir = Path(__file__).parent.parent
    builtin_dir = builtin_templates_dir or pkg_dir / "templates"

    # Initialize user data
    udm = UserDataManager(base_dir=user_data_dir)
    udm.init()

    # Create AgentForge with built-in templates
    forge = AgentForge(base_dir=builtin_dir.parent)
    forge.templates._templates_dir = builtin_dir
    forge.init()

    # Load user templates (merge)
    user_registry = AgentForge(base_dir=udm.base_dir)
    user_registry.templates._templates_dir = udm.templates_dir
    user_registry.init()
    for t in user_registry.templates.list():
        if t.id not in {bt.id for bt in forge.templates.list()}:
            forge.templates.register(t)

    # Create MCP server
    server = FastMCP("agent-forge")

    # Register all tools
    register_lifecycle_tools(server, forge)
    register_template_tools(server, forge, udm.templates_dir)
    register_chat_tools(server, forge)
    register_cooperation_tools(server, forge)

    return server, forge


def main():
    server, _ = create_server()
    server.run(transport="stdio")


if __name__ == "__main__":
    main()
