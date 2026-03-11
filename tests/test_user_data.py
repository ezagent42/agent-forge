import pytest
from pathlib import Path
from agent_forge.user_data import UserDataManager


@pytest.fixture
def udm(tmp_path):
    return UserDataManager(base_dir=tmp_path)


def test_init_creates_directories(udm, tmp_path):
    udm.init()
    assert (tmp_path / "templates").is_dir()
    assert (tmp_path / "instances").is_dir()
    assert (tmp_path / "logs").is_dir()


def test_init_creates_default_config(udm, tmp_path):
    udm.init()
    config_path = tmp_path / "config.toml"
    assert config_path.exists()
    content = config_path.read_text()
    assert "adapter" in content


def test_init_does_not_overwrite_existing_config(udm, tmp_path):
    config_path = tmp_path / "config.toml"
    config_path.write_text('custom = "value"')
    udm.init()
    assert 'custom = "value"' in config_path.read_text()


def test_load_config(udm, tmp_path):
    udm.init()
    config = udm.load_config()
    assert "adapter" in config
    assert config["adapter"]["default"] == "claude"


def test_templates_dir(udm, tmp_path):
    assert udm.templates_dir == tmp_path / "templates"


def test_instances_dir(udm, tmp_path):
    assert udm.instances_dir == tmp_path / "instances"
