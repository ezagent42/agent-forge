# tests/test_mcp_server.py
import pytest
from pathlib import Path


def test_create_server(tmp_path):
    from agent_forge.mcp_server import create_server
    server, forge = create_server(
        builtin_templates_dir=tmp_path / "templates",
        user_data_dir=tmp_path / "user",
    )
    assert server is not None
    assert forge is not None


def test_server_has_tools(tmp_path):
    from agent_forge.mcp_server import create_server
    (tmp_path / "templates").mkdir()
    server, forge = create_server(
        builtin_templates_dir=tmp_path / "templates",
        user_data_dir=tmp_path / "user",
    )
    assert forge.templates is not None
