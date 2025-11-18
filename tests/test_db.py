"""Tests for database initialization and session management."""

from pathlib import Path

from sqlalchemy import text

from dot.db import get_engine, get_session, get_session_factory
from dot.settings import Settings


def test_get_engine_creates_database_file(tmp_path: Path) -> None:
    """Test that get_engine creates the database file."""
    custom_home = tmp_path / "test_dot"
    settings = Settings(dot_home=custom_home)

    engine = get_engine(settings)

    # Should be able to connect (this creates the database file)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        assert result.scalar() == 1

    # Database file should now exist
    assert settings.db_path.exists()
    assert settings.db_path.is_file()


def test_get_session_factory_creates_sessions(tmp_path: Path) -> None:
    """Test that session factory creates working sessions."""
    custom_home = tmp_path / "test_dot"
    settings = Settings(dot_home=custom_home)

    factory = get_session_factory(settings)
    session = factory()

    try:
        # Should be able to execute queries
        result = session.execute(text("SELECT 1"))
        assert result.scalar() == 1
    finally:
        session.close()


def test_get_session_context_manager(tmp_path: Path) -> None:
    """Test that get_session works as context manager."""
    custom_home = tmp_path / "test_dot"
    settings = Settings(dot_home=custom_home)

    # Use the generator as intended
    gen = get_session(settings)
    session = next(gen)

    try:
        # Should be able to use the session
        result = session.execute(text("SELECT 1"))
        assert result.scalar() == 1
    finally:
        # Close the generator
        try:
            next(gen)
        except StopIteration:
            pass


def test_multiple_sessions_same_database(tmp_path: Path) -> None:
    """Test that multiple sessions can access the same database."""
    custom_home = tmp_path / "test_dot"
    settings = Settings(dot_home=custom_home)

    factory = get_session_factory(settings)

    session1 = factory()
    session2 = factory()

    try:
        result1 = session1.execute(text("SELECT 1"))
        result2 = session2.execute(text("SELECT 2"))

        assert result1.scalar() == 1
        assert result2.scalar() == 2
    finally:
        session1.close()
        session2.close()
