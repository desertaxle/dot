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

        # List by today's date
        from datetime import date

        today = date.today()
        today_tasks = repo.list_by_date(today)

        assert len(today_tasks) == 2
        assert any(t.id == task1.id for t in today_tasks)
        assert any(t.id == task2.id for t in today_tasks)

        # List by a different date - should be empty
        from datetime import timedelta

        yesterday = today - timedelta(days=1)
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
