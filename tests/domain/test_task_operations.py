"""Tests for task operations."""

from uuid import uuid4

import pytest

from dot.domain.models import TaskStatus
from dot.domain.task_operations import (
    cancel_task,
    complete_task,
    create_task,
    reopen_task,
    set_priority,
    update_task,
)
from dot.domain.validation import InvalidTaskError


class TestCreateTask:
    """Tests for create_task operation."""

    def test_create_basic_task(self):
        """Create a task with minimal parameters."""
        task_id = uuid4()
        task = create_task(id=task_id, title="Buy milk")
        assert task.id == task_id
        assert task.title == "Buy milk"
        assert task.status == TaskStatus.TODO
        assert task.description is None
        assert task.priority is None

    def test_create_task_with_description(self):
        """Create a task with description."""
        task = create_task(id=uuid4(), title="Buy milk", description="Whole milk, 1L")
        assert task.description == "Whole milk, 1L"

    def test_create_task_with_priority(self):
        """Create a task with priority."""
        task = create_task(id=uuid4(), title="Buy milk", priority=1)
        assert task.priority == 1

    def test_create_task_empty_title_raises(self):
        """Creating task with empty title raises error."""
        with pytest.raises(InvalidTaskError):
            create_task(id=uuid4(), title="")

    def test_create_task_invalid_priority_raises(self):
        """Creating task with invalid priority raises error."""
        with pytest.raises(InvalidTaskError):
            create_task(id=uuid4(), title="Test", priority=5)


class TestCompleteTask:
    """Tests for complete_task operation."""

    def test_complete_todo_task(self):
        """Completing a TODO task marks it DONE."""
        task = create_task(id=uuid4(), title="Test")
        completed = complete_task(task)
        assert completed.status == TaskStatus.DONE
        assert completed.id == task.id  # Other fields unchanged

    def test_complete_already_done_raises(self):
        """Completing an already-done task raises error."""
        task = create_task(id=uuid4(), title="Test")
        completed = complete_task(task)
        with pytest.raises(InvalidTaskError, match="already completed"):
            complete_task(completed)

    def test_complete_cancelled_task(self):
        """Can complete a cancelled task (reactivate)."""
        task = create_task(id=uuid4(), title="Test")
        cancelled = cancel_task(task)
        # Can't complete cancelled directly, must reopen first
        reopened = reopen_task(cancelled)
        completed = complete_task(reopened)
        assert completed.status == TaskStatus.DONE


class TestCancelTask:
    """Tests for cancel_task operation."""

    def test_cancel_todo_task(self):
        """Cancelling a TODO task marks it CANCELLED."""
        task = create_task(id=uuid4(), title="Test")
        cancelled = cancel_task(task)
        assert cancelled.status == TaskStatus.CANCELLED

    def test_cancel_already_cancelled_raises(self):
        """Cancelling an already-cancelled task raises error."""
        task = create_task(id=uuid4(), title="Test")
        cancelled = cancel_task(task)
        with pytest.raises(InvalidTaskError, match="already cancelled"):
            cancel_task(cancelled)

    def test_cancel_done_task(self):
        """Can cancel a done task (uncomplete it)."""
        task = create_task(id=uuid4(), title="Test")
        completed = complete_task(task)
        # Can't cancel done directly, must reopen first
        reopened = reopen_task(completed)
        cancelled = cancel_task(reopened)
        assert cancelled.status == TaskStatus.CANCELLED


class TestReopenTask:
    """Tests for reopen_task operation."""

    def test_reopen_done_task(self):
        """Reopening a DONE task returns it to TODO."""
        task = create_task(id=uuid4(), title="Test")
        completed = complete_task(task)
        reopened = reopen_task(completed)
        assert reopened.status == TaskStatus.TODO

    def test_reopen_cancelled_task(self):
        """Reopening a CANCELLED task returns it to TODO."""
        task = create_task(id=uuid4(), title="Test")
        cancelled = cancel_task(task)
        reopened = reopen_task(cancelled)
        assert reopened.status == TaskStatus.TODO

    def test_reopen_todo_task_raises(self):
        """Reopening a TODO task raises error."""
        task = create_task(id=uuid4(), title="Test")
        with pytest.raises(InvalidTaskError, match="already open"):
            reopen_task(task)


class TestUpdateTask:
    """Tests for update_task operation."""

    def test_update_title(self):
        """Updating title changes task title."""
        task = create_task(id=uuid4(), title="Old title")
        updated = update_task(task, title="New title")
        assert updated.title == "New title"

    def test_update_description(self):
        """Updating description changes task description."""
        task = create_task(id=uuid4(), title="Test")
        updated = update_task(task, description="New description")
        assert updated.description == "New description"

    def test_update_priority(self):
        """Updating priority changes task priority."""
        task = create_task(id=uuid4(), title="Test")
        updated = update_task(task, priority=2)
        assert updated.priority == 2

    def test_update_multiple_fields(self):
        """Can update multiple fields at once."""
        task = create_task(id=uuid4(), title="Old", priority=3)
        updated = update_task(task, title="New", priority=1)
        assert updated.title == "New"
        assert updated.priority == 1

    def test_update_with_none_preserves_original(self):
        """Updating with None values preserves original."""
        task = create_task(id=uuid4(), title="Title", priority=2)
        updated = update_task(task, title=None, priority=None)
        assert updated.title == "Title"
        assert updated.priority == 2

    def test_update_empty_title_raises(self):
        """Updating with empty title raises error."""
        task = create_task(id=uuid4(), title="Test")
        with pytest.raises(InvalidTaskError):
            update_task(task, title="")


class TestSetPriority:
    """Tests for set_priority operation."""

    def test_set_priority_on_task(self):
        """Setting priority updates the priority."""
        task = create_task(id=uuid4(), title="Test")
        updated = set_priority(task, 2)
        assert updated.priority == 2

    def test_set_priority_to_none(self):
        """Setting priority to None clears it."""
        task = create_task(id=uuid4(), title="Test", priority=1)
        updated = set_priority(task, None)
        assert updated.priority is None

    def test_set_invalid_priority_raises(self):
        """Setting invalid priority raises error."""
        task = create_task(id=uuid4(), title="Test")
        with pytest.raises(InvalidTaskError):
            set_priority(task, 5)


class TestTaskStateMachine:
    """Tests for task state transitions."""

    def test_todo_to_done_to_todo(self):
        """Task can transition TODO → DONE → TODO."""
        task = create_task(id=uuid4(), title="Test")
        assert task.status == TaskStatus.TODO

        done = complete_task(task)
        assert done.status == TaskStatus.DONE

        reopened = reopen_task(done)
        assert reopened.status == TaskStatus.TODO

    def test_todo_to_cancelled_to_todo(self):
        """Task can transition TODO → CANCELLED → TODO."""
        task = create_task(id=uuid4(), title="Test")
        cancelled = cancel_task(task)
        assert cancelled.status == TaskStatus.CANCELLED

        reopened = reopen_task(cancelled)
        assert reopened.status == TaskStatus.TODO

    def test_all_valid_transitions(self):
        """Verify all valid state transitions."""
        task = create_task(id=uuid4(), title="Test")

        # TODO → DONE
        done = complete_task(task)
        assert done.status == TaskStatus.DONE

        # DONE → TODO
        todo = reopen_task(done)
        assert todo.status == TaskStatus.TODO

        # TODO → CANCELLED
        cancelled = cancel_task(todo)
        assert cancelled.status == TaskStatus.CANCELLED

        # CANCELLED → TODO
        todo2 = reopen_task(cancelled)
        assert todo2.status == TaskStatus.TODO
