"""Database initialization and session management."""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from dot.settings import Settings


def get_engine(settings: Settings):
    """Create a SQLAlchemy engine for the configured database.

    Args:
        settings: Application settings containing database path

    Returns:
        SQLAlchemy engine instance
    """
    settings.ensure_dot_home_exists()
    database_url = f"sqlite:///{settings.db_path}"
    return create_engine(database_url, echo=False)


def get_session_factory(settings: Settings) -> sessionmaker[Session]:
    """Create a session factory for database operations.

    Args:
        settings: Application settings

    Returns:
        Session factory
    """
    engine = get_engine(settings)
    return sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_session(settings: Settings) -> Generator[Session, None, None]:
    """Get a database session with automatic cleanup.

    Args:
        settings: Application settings

    Yields:
        Database session
    """
    factory = get_session_factory(settings)
    session = factory()
    try:
        yield session
    finally:
        session.close()
