"""Tests for settings configuration."""

from pathlib import Path

import pytest

from dot.settings import Settings


def test_settings_default_dot_home() -> None:
    """Test that default dot_home is ~/.dot."""
    settings = Settings()
    expected = Path.home() / ".dot"
    assert settings.dot_home == expected


def test_settings_db_path_property() -> None:
    """Test that db_path returns correct path."""
    settings = Settings()
    expected = settings.dot_home / "dot.db"
    assert settings.db_path == expected


def test_settings_custom_dot_home(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Test that DOT_HOME environment variable overrides default."""
    custom_home = tmp_path / "custom_dot"
    monkeypatch.setenv("DOT_HOME", str(custom_home))

    settings = Settings()
    assert settings.dot_home == custom_home
    assert settings.db_path == custom_home / "dot.db"


def test_ensure_dot_home_creates_directory(tmp_path: Path) -> None:
    """Test that ensure_dot_home_exists creates the directory."""
    custom_home = tmp_path / "test_dot"
    settings = Settings(dot_home=custom_home)

    assert not custom_home.exists()

    settings.ensure_dot_home_exists()

    assert custom_home.exists()
    assert custom_home.is_dir()


def test_ensure_dot_home_idempotent(tmp_path: Path) -> None:
    """Test that ensure_dot_home_exists can be called multiple times."""
    custom_home = tmp_path / "test_dot"
    settings = Settings(dot_home=custom_home)

    settings.ensure_dot_home_exists()
    settings.ensure_dot_home_exists()  # Should not raise

    assert custom_home.exists()
