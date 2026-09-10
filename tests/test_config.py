"""Tests for gh-pulse config."""

import tempfile
from pathlib import Path

from gh_pulse.config import Config


def test_default_config():
    config = Config()
    assert config.repos == []
    assert config.refresh_interval == 60
    assert config.show_drafts is False
    assert config.show_closed is False
    assert config.max_prs_per_repo == 20


def test_config_from_file():
    config_content = """
repos:
  - owner/repo1
  - owner/repo2
refresh_interval: 30
show_drafts: true
"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(config_content)
        config_path = f.name

    try:
        config = Config.load(config_path)
        assert config.repos == ['owner/repo1', 'owner/repo2']
        assert config.refresh_interval == 30
        assert config.show_drafts is True
        assert config.show_closed is False
    finally:
        Path(config_path).unlink()


def test_config_save_and_load():
    config = Config(repos=['owner/repo1'], refresh_interval=45, show_drafts=True)
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        config_path = f.name

    try:
        config.save(config_path)
        loaded = Config.load(config_path)
        assert loaded.repos == ['owner/repo1']
        assert loaded.refresh_interval == 45
        assert loaded.show_drafts is True
    finally:
        Path(config_path).unlink()


def test_config_missing_file_uses_defaults():
    config = Config.load('/nonexistent/path/config.yaml')
    assert config.repos == []
    assert config.refresh_interval == 60


def test_config_partial():
    config_content = """
repos:
  - owner/repo1
"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(config_content)
        config_path = f.name

    try:
        config = Config.load(config_path)
        assert config.repos == ['owner/repo1']
        assert config.refresh_interval == 60  # default
        assert config.show_drafts is False  # default
    finally:
        Path(config_path).unlink()
