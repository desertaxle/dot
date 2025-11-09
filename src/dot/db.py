"""Database initialization and session management."""

from pathlib import Path
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from .settings import settings
from .models import Base


class Database:
    """Manages SQLite database connection and sessions."""

    def __init__(self, db_path: Path):
        """Initialize the database with a given path.

        Args:
            db_path: Path to the SQLite database file.
        """
        self.db_path = db_path
        self.engine = None
        self.SessionLocal = None

    def initialize(self) -> None:
        """Initialize the database engine and create tables if they don't exist."""
        # Create the database URL for SQLite
        db_url = f"sqlite:///{self.db_path}"

        # Create the engine
        self.engine = create_engine(
            db_url,
            connect_args={"check_same_thread": False},  # Needed for SQLite
            echo=False,  # Set to True for SQL debugging
        )

        # Create session factory
        self.SessionLocal = sessionmaker(bind=self.engine, expire_on_commit=False)

        # Create all tables
        Base.metadata.create_all(bind=self.engine)

    def get_session(self) -> Generator[Session, None, None]:
        """Get a database session.

        Yields:
            A SQLAlchemy session.
        """
        if self.SessionLocal is None:
            raise RuntimeError("Database not initialized. Call initialize() first.")

        session = self.SessionLocal()
        try:
            yield session
        finally:
            session.close()

    def close(self) -> None:
        """Close the database connection."""
        if self.engine:
            self.engine.dispose()


# Global database instance
_db: Database | None = None


def get_database() -> Database:
    """Get the global database instance.

    Returns:
        The global Database instance.

    Raises:
        RuntimeError: If the database hasn't been initialized yet.
    """
    if _db is None:
        return init_database(settings.db_path)
    return _db


def init_database(db_path: Path) -> Database:
    """Initialize the global database instance.

    Args:
        db_path: Path to the SQLite database file.

    Returns:
        The initialized Database instance.
    """
    global _db
    _db = Database(db_path)
    _db.initialize()
    return _db
