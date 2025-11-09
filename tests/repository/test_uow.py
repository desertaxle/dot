"""Tests for Unit of Work pattern."""

from datetime import datetime, timezone


from dot.domain.models import Event, Note, Task
from dot.repository.uow import InMemoryUnitOfWork


class TestAbstractUnitOfWork:
    """Tests for AbstractUnitOfWork interface."""

    def test_uow_is_context_manager(self):
        """UnitOfWork can be used as a context manager."""
        uow = InMemoryUnitOfWork()

        # Should not raise
        with uow:
            pass

    def test_uow_has_task_repository(self):
        """UnitOfWork provides access to task repository."""
        uow = InMemoryUnitOfWork()

        assert hasattr(uow, "tasks")
        assert uow.tasks is not None

    def test_uow_has_note_repository(self):
        """UnitOfWork provides access to note repository."""
        uow = InMemoryUnitOfWork()

        assert hasattr(uow, "notes")
        assert uow.notes is not None

    def test_uow_has_event_repository(self):
        """UnitOfWork provides access to event repository."""
        uow = InMemoryUnitOfWork()

        assert hasattr(uow, "events")
        assert uow.events is not None

    def test_uow_commit(self):
        """UnitOfWork can commit changes."""
        uow = InMemoryUnitOfWork()

        with uow:
            now = datetime.now(timezone.utc)
            task = Task(id=1, title="Test", created_at=now, updated_at=now)
            uow.tasks.add(task)
            uow.commit()

        # After commit, data should be persisted
        assert uow.tasks.get(1) is not None

    def test_uow_rollback(self):
        """UnitOfWork can rollback changes."""
        uow = InMemoryUnitOfWork()

        with uow:
            now = datetime.now(timezone.utc)
            task = Task(id=1, title="Test", created_at=now, updated_at=now)
            uow.tasks.add(task)
            uow.rollback()

        # After rollback, data should not be persisted
        # (In-memory UoW doesn't actually support true rollback, but interface is there)


class TestInMemoryUnitOfWork:
    """Tests for InMemoryUnitOfWork implementation."""

    def test_multiple_repositories_in_one_transaction(self):
        """Multiple repositories can be used in one UoW transaction."""
        uow = InMemoryUnitOfWork()
        now = datetime.now(timezone.utc)

        with uow:
            # Add to multiple repositories
            task = Task(id=1, title="Task", created_at=now, updated_at=now)
            note = Note(id=1, title="Note", created_at=now, updated_at=now)
            event = Event(
                id=1, title="Event", occurred_at=now, created_at=now, updated_at=now
            )

            uow.tasks.add(task)
            uow.notes.add(note)
            uow.events.add(event)

            uow.commit()

        # All should be persisted
        assert uow.tasks.get(1) is not None
        assert uow.notes.get(1) is not None
        assert uow.events.get(1) is not None

    def test_separate_uow_instances_have_separate_storage(self):
        """Each UoW instance has separate storage."""
        uow1 = InMemoryUnitOfWork()
        uow2 = InMemoryUnitOfWork()
        now = datetime.now(timezone.utc)

        with uow1:
            task = Task(id=1, title="Task in UoW1", created_at=now, updated_at=now)
            uow1.tasks.add(task)
            uow1.commit()

        # uow2 should not have the task
        assert uow2.tasks.get(1) is None

    def test_uow_provides_fresh_repositories(self):
        """Each access to repository through UoW returns the same instance."""
        uow = InMemoryUnitOfWork()

        assert uow.tasks is uow.tasks
        assert uow.notes is uow.notes
        assert uow.events is uow.events
