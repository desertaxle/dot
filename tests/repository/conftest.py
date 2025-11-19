"""Pytest fixtures for repository tests."""

from pathlib import Path

import pytest
from sqlalchemy.orm import Session

from dot.db import get_session_factory
from dot.models import Base
from dot.repository.memory import InMemoryTaskRepository
from dot.settings import Settings


@pytest.fixture(params=["memory", "sqlalchemy"])
def task_repository(request, tmp_path: Path):
    """Provide both in-memory and SQLAlchemy repository implementations.

    This fixture parametrizes tests to run against both implementations,
    ensuring they conform to the same contract.
    """
    if request.param == "memory":
        yield InMemoryTaskRepository()
    elif request.param == "sqlalchemy":
        # Set up temporary database
        settings = Settings(dot_home=tmp_path / "test_dot")
        factory = get_session_factory(settings)

        # Create tables
        engine = factory.kw["bind"]
        Base.metadata.create_all(engine)

        # Create session
        session: Session = factory()

        # Create repository
        from dot.repository.sqlalchemy import SQLAlchemyTaskRepository

        repo = SQLAlchemyTaskRepository(session)

        yield repo

        # Cleanup
        session.close()
        Base.metadata.drop_all(engine)
    else:
        raise ValueError(f"Unknown repository type: {request.param}")


@pytest.fixture(params=["memory", "sqlalchemy"])
def event_repository(request, tmp_path: Path):
    """Provide both in-memory and SQLAlchemy event repository implementations.

    This fixture parametrizes tests to run against both implementations,
    ensuring they conform to the same contract.
    """
    if request.param == "memory":
        from dot.repository.memory import InMemoryEventRepository

        yield InMemoryEventRepository()
    elif request.param == "sqlalchemy":
        # Set up temporary database
        settings = Settings(dot_home=tmp_path / "test_dot")
        factory = get_session_factory(settings)

        # Create tables
        engine = factory.kw["bind"]
        Base.metadata.create_all(engine)

        # Create session
        session: Session = factory()

        # Create repository
        from dot.repository.sqlalchemy import SQLAlchemyEventRepository

        repo = SQLAlchemyEventRepository(session)

        yield repo

        # Cleanup
        session.close()
        Base.metadata.drop_all(engine)
    else:
        raise ValueError(f"Unknown repository type: {request.param}")
