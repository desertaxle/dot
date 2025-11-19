"""Integration tests for end-to-end workflows with real database."""

import tempfile
from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from dot.domain.models import TaskStatus
from dot.domain.operations import create_task, mark_cancelled, mark_done
from dot.models import Base
from dot.repository.sqlalchemy import SQLAlchemyTaskRepository


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        engine = create_engine(f"sqlite:///{db_path}")
        Base.metadata.create_all(engine)
        SessionFactory = sessionmaker(bind=engine)
        yield SessionFactory
        Base.metadata.drop_all(engine)
        engine.dispose()


def test_task_workflow_create_list_done(temp_db):
    """Test complete task workflow: create → list → mark done → list."""
    session = temp_db()

    try:
        repo = SQLAlchemyTaskRepository(session)

        # Create a task
        task = create_task("Buy groceries", description="Milk, eggs, bread")
        repo.add(task)

        # List all tasks - should have one TODO task
        all_tasks = repo.list()
        assert len(all_tasks) == 1
        assert all_tasks[0].title == "Buy groceries"
        assert all_tasks[0].status == TaskStatus.TODO

        # List TODO tasks specifically
        todo_tasks = repo.list(status=TaskStatus.TODO)
        assert len(todo_tasks) == 1

        # List DONE tasks - should be empty
        done_tasks = repo.list(status=TaskStatus.DONE)
        assert len(done_tasks) == 0

        # Mark task as done
        done_task = mark_done(task)
        repo.update(done_task)

        # List all tasks again
        all_tasks = repo.list()
        assert len(all_tasks) == 1
        assert all_tasks[0].status == TaskStatus.DONE

        # List TODO tasks - should be empty now
        todo_tasks = repo.list(status=TaskStatus.TODO)
        assert len(todo_tasks) == 0

        # List DONE tasks - should have our task
        done_tasks = repo.list(status=TaskStatus.DONE)
        assert len(done_tasks) == 1
        assert done_tasks[0].title == "Buy groceries"

    finally:
        session.close()


def test_task_workflow_create_multiple_filter(temp_db):
    """Test creating multiple tasks and filtering by status."""
    session = temp_db()

    try:
        repo = SQLAlchemyTaskRepository(session)

        # Create multiple tasks
        task1 = create_task("Task 1")
        task2 = create_task("Task 2")
        task3 = create_task("Task 3")

        repo.add(task1)
        repo.add(task2)
        repo.add(task3)

        # All should be TODO
        all_tasks = repo.list()
        assert len(all_tasks) == 3

        # Mark one as done, one as cancelled
        done_task = mark_done(task1)
        repo.update(done_task)

        cancelled_task = mark_cancelled(task2)
        repo.update(cancelled_task)

        # Check filtering
        todo_tasks = repo.list(status=TaskStatus.TODO)
        assert len(todo_tasks) == 1
        assert todo_tasks[0].id == task3.id

        done_tasks = repo.list(status=TaskStatus.DONE)
        assert len(done_tasks) == 1
        assert done_tasks[0].id == task1.id

        cancelled_tasks = repo.list(status=TaskStatus.CANCELLED)
        assert len(cancelled_tasks) == 1
        assert cancelled_tasks[0].id == task2.id

    finally:
        session.close()


def test_task_workflow_get_by_id(temp_db):
    """Test creating and retrieving a task by ID."""
    session = temp_db()

    try:
        repo = SQLAlchemyTaskRepository(session)

        # Create and add task
        task = create_task("Test task")
        repo.add(task)

        # Retrieve by ID
        retrieved_task = repo.get(task.id)
        assert retrieved_task is not None
        assert retrieved_task.id == task.id
        assert retrieved_task.title == task.title
        assert retrieved_task.status == TaskStatus.TODO

        # Try to retrieve non-existent task
        from uuid import uuid4

        non_existent = repo.get(uuid4())
        assert non_existent is None

    finally:
        session.close()


def test_task_workflow_delete(temp_db):
    """Test deleting a task."""
    session = temp_db()

    try:
        repo = SQLAlchemyTaskRepository(session)

        # Create and add task
        task = create_task("Task to delete")
        repo.add(task)

        # Verify it exists
        assert len(repo.list()) == 1

        # Delete it
        repo.delete(task.id)

        # Verify it's gone
        assert len(repo.list()) == 0
        assert repo.get(task.id) is None

    finally:
        session.close()


def test_task_workflow_list_by_date(temp_db):
    """Test listing tasks by creation date."""
    session = temp_db()

    try:
        repo = SQLAlchemyTaskRepository(session)

        # Create tasks
        task1 = create_task("Task 1")
        task2 = create_task("Task 2")

        repo.add(task1)
        repo.add(task2)

        # List by today's date (UTC, since create_task uses utcnow)
        from datetime import datetime

        today_utc = datetime.utcnow().date()
        today_tasks = repo.list_by_date(today_utc)

        assert len(today_tasks) == 2
        assert any(t.id == task1.id for t in today_tasks)
        assert any(t.id == task2.id for t in today_tasks)

        # List by a different date - should be empty
        from datetime import timedelta

        yesterday = today_utc - timedelta(days=1)
        yesterday_tasks = repo.list_by_date(yesterday)
        assert len(yesterday_tasks) == 0

    finally:
        session.close()


def test_task_workflow_state_transitions(temp_db):
    """Test all possible task state transitions."""
    session = temp_db()

    try:
        repo = SQLAlchemyTaskRepository(session)

        # Create task (starts as TODO)
        task = create_task("State transition test")
        repo.add(task)
        assert task.status == TaskStatus.TODO

        # TODO -> DONE
        task = mark_done(task)
        repo.update(task)
        retrieved = repo.get(task.id)
        assert retrieved.status == TaskStatus.DONE

        # DONE -> CANCELLED
        task = mark_cancelled(task)
        repo.update(task)
        retrieved = repo.get(task.id)
        assert retrieved.status == TaskStatus.CANCELLED

        # CANCELLED -> TODO (reopen)
        from dot.domain.operations import reopen_task

        task = reopen_task(task)
        repo.update(task)
        retrieved = repo.get(task.id)
        assert retrieved.status == TaskStatus.TODO

        # TODO -> CANCELLED
        task = mark_cancelled(task)
        repo.update(task)
        retrieved = repo.get(task.id)
        assert retrieved.status == TaskStatus.CANCELLED

    finally:
        session.close()


def test_task_workflow_persistence(temp_db):
    """Test that tasks persist across sessions."""
    # First session: create and save task
    session1 = temp_db()
    repo1 = SQLAlchemyTaskRepository(session1)

    task = create_task("Persistent task", description="This should persist")
    repo1.add(task)
    task_id = task.id
    session1.close()

    # Second session: retrieve the same task
    session2 = temp_db()
    repo2 = SQLAlchemyTaskRepository(session2)

    retrieved_task = repo2.get(task_id)
    assert retrieved_task is not None
    assert retrieved_task.id == task_id
    assert retrieved_task.title == "Persistent task"
    assert retrieved_task.description == "This should persist"
    assert retrieved_task.status == TaskStatus.TODO
    session2.close()


def test_task_workflow_update_preserves_id(temp_db):
    """Test that updating a task preserves its ID and created_at."""
    session = temp_db()

    try:
        repo = SQLAlchemyTaskRepository(session)

        # Create task
        task = create_task("Original task")
        repo.add(task)
        original_id = task.id
        original_created_at = task.created_at

        # Mark as done
        updated_task = mark_done(task)
        repo.update(updated_task)

        # Retrieve and verify
        retrieved = repo.get(original_id)
        assert retrieved is not None
        assert retrieved.id == original_id
        assert retrieved.created_at == original_created_at
        assert retrieved.status == TaskStatus.DONE
        assert retrieved.updated_at > original_created_at

    finally:
        session.close()


# Event Workflow Tests


def test_event_workflow_create_and_list(temp_db):
    """Test complete event workflow: create → list."""

    from dot.domain.operations import create_event
    from dot.repository.sqlalchemy import SQLAlchemyEventRepository

    session = temp_db()

    try:
        repo = SQLAlchemyEventRepository(session)

        # Create an event
        event = create_event("Team Meeting", description="Quarterly review")
        repo.add(event)

        # List all events
        all_events = repo.list()
        assert len(all_events) == 1
        assert all_events[0].title == "Team Meeting"
        assert all_events[0].description == "Quarterly review"

    finally:
        session.close()


def test_event_workflow_list_by_date(temp_db):
    """Test listing events by date."""
    from datetime import datetime, timedelta

    from dot.domain.operations import create_event
    from dot.repository.sqlalchemy import SQLAlchemyEventRepository

    session = temp_db()

    try:
        repo = SQLAlchemyEventRepository(session)

        # Create events on different dates
        today = datetime.now()
        yesterday = today - timedelta(days=1)

        event1 = create_event("Today's Event", occurred_at=today)
        event2 = create_event("Yesterday's Event", occurred_at=yesterday)

        repo.add(event1)
        repo.add(event2)

        # List events for today
        today_events = repo.list_by_date(today.date())
        assert len(today_events) == 1
        assert today_events[0].title == "Today's Event"

        # List events for yesterday
        yesterday_events = repo.list_by_date(yesterday.date())
        assert len(yesterday_events) == 1
        assert yesterday_events[0].title == "Yesterday's Event"

    finally:
        session.close()


def test_event_workflow_list_by_range(temp_db):
    """Test listing events by date range."""
    from datetime import datetime, timedelta

    from dot.domain.operations import create_event
    from dot.repository.sqlalchemy import SQLAlchemyEventRepository

    session = temp_db()

    try:
        repo = SQLAlchemyEventRepository(session)

        # Create events across multiple dates
        base_date = datetime(2025, 11, 15, 10, 0)

        event1 = create_event("Event 1", occurred_at=base_date)
        event2 = create_event("Event 2", occurred_at=base_date + timedelta(days=1))
        event3 = create_event("Event 3", occurred_at=base_date + timedelta(days=2))
        event4 = create_event("Event 4", occurred_at=base_date + timedelta(days=10))

        repo.add(event1)
        repo.add(event2)
        repo.add(event3)
        repo.add(event4)

        # Query range that includes first 3 events
        start_date = base_date.date()
        end_date = (base_date + timedelta(days=2)).date()

        range_events = repo.list_by_range(start_date, end_date)
        assert len(range_events) == 3
        assert any(e.title == "Event 1" for e in range_events)
        assert any(e.title == "Event 2" for e in range_events)
        assert any(e.title == "Event 3" for e in range_events)
        assert not any(e.title == "Event 4" for e in range_events)

    finally:
        session.close()


def test_event_workflow_get_by_id(temp_db):
    """Test creating and retrieving an event by ID."""
    from dot.domain.operations import create_event
    from dot.repository.sqlalchemy import SQLAlchemyEventRepository

    session = temp_db()

    try:
        repo = SQLAlchemyEventRepository(session)

        # Create and add event
        event = create_event("Conference", description="Annual tech conference")
        repo.add(event)

        # Retrieve by ID
        retrieved_event = repo.get(event.id)
        assert retrieved_event is not None
        assert retrieved_event.id == event.id
        assert retrieved_event.title == event.title
        assert retrieved_event.description == "Annual tech conference"

        # Try to retrieve non-existent event
        from uuid import uuid4

        non_existent = repo.get(uuid4())
        assert non_existent is None

    finally:
        session.close()


def test_event_workflow_delete(temp_db):
    """Test deleting an event."""
    from dot.domain.operations import create_event
    from dot.repository.sqlalchemy import SQLAlchemyEventRepository

    session = temp_db()

    try:
        repo = SQLAlchemyEventRepository(session)

        # Create and add event
        event = create_event("Event to delete")
        repo.add(event)

        # Verify it exists
        assert len(repo.list()) == 1

        # Delete it
        repo.delete(event.id)

        # Verify it's gone
        assert len(repo.list()) == 0
        assert repo.get(event.id) is None

    finally:
        session.close()


def test_event_workflow_chronological_sorting(temp_db):
    """Test that events are sorted chronologically by occurred_at."""
    from datetime import datetime, timedelta

    from dot.domain.operations import create_event
    from dot.repository.sqlalchemy import SQLAlchemyEventRepository

    session = temp_db()

    try:
        repo = SQLAlchemyEventRepository(session)

        # Create events in non-chronological order
        base_date = datetime(2025, 11, 15, 10, 0)

        event2 = create_event(
            "Second Event", occurred_at=base_date + timedelta(hours=2)
        )
        event1 = create_event("First Event", occurred_at=base_date)
        event3 = create_event("Third Event", occurred_at=base_date + timedelta(hours=4))

        # Add in random order
        repo.add(event2)
        repo.add(event1)
        repo.add(event3)

        # List should be chronologically sorted
        events = repo.list()
        assert len(events) == 3
        assert events[0].title == "First Event"
        assert events[1].title == "Second Event"
        assert events[2].title == "Third Event"

    finally:
        session.close()


def test_event_workflow_persistence(temp_db):
    """Test that events persist across sessions."""
    from dot.domain.operations import create_event
    from dot.repository.sqlalchemy import SQLAlchemyEventRepository

    # First session: create and save event
    session1 = temp_db()
    repo1 = SQLAlchemyEventRepository(session1)

    event = create_event("Persistent event", description="This should persist")
    repo1.add(event)
    event_id = event.id
    session1.close()

    # Second session: retrieve the same event
    session2 = temp_db()
    repo2 = SQLAlchemyEventRepository(session2)

    retrieved_event = repo2.get(event_id)
    assert retrieved_event is not None
    assert retrieved_event.id == event_id
    assert retrieved_event.title == "Persistent event"
    assert retrieved_event.description == "This should persist"
    session2.close()
