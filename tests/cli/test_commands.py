"""Tests for CLI commands."""

from pathlib import Path
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest

from dot.domain.models import Task, TaskStatus


@pytest.fixture
def mock_settings():
    """Create a mock Settings object."""
    settings = MagicMock()
    settings.dot_home = MagicMock()
    settings.db_path = MagicMock()
    settings.ensure_dot_home_exists = MagicMock()
    return settings


@pytest.fixture
def mock_session():
    """Create a mock database session."""
    session = MagicMock()
    return session


@pytest.fixture
def mock_repository():
    """Create a mock task repository."""
    repo = MagicMock()
    return repo


def test_task_create_success(mock_settings, mock_session, mock_repository):
    """Test creating a task successfully."""
    with (
        patch("dot.__main__.Settings", return_value=mock_settings),
        patch("dot.__main__.get_session") as mock_get_session,
        patch("dot.__main__.SQLAlchemyTaskRepository", return_value=mock_repository),
        patch("dot.__main__._init_database"),
        patch("dot.__main__.create_task") as mock_create,
        patch("dot.__main__.console") as mock_console,
    ):
        # Setup
        task = Task(
            id=uuid4(),
            title="Test Task",
            description=None,
            status=TaskStatus.TODO,
            created_at=MagicMock(),
            updated_at=MagicMock(),
        )
        mock_create.return_value = task
        mock_get_session.return_value = iter([mock_session])

        # Import and run command
        from dot.__main__ import task_app

        # Run the create command
        with pytest.raises(SystemExit) as exc_info:
            task_app(["create", "Test Task"])

        # Assertions
        assert exc_info.value.code == 0  # type: ignore[unresolved-attribute]
        mock_create.assert_called_once_with("Test Task", None)
        mock_repository.add.assert_called_once()
        mock_console.print.assert_any_call("✓ Task created: Test Task", style="green")


def test_task_create_with_description(mock_settings, mock_session, mock_repository):
    """Test creating a task with a description."""
    with (
        patch("dot.__main__.Settings", return_value=mock_settings),
        patch("dot.__main__.get_session") as mock_get_session,
        patch("dot.__main__.SQLAlchemyTaskRepository", return_value=mock_repository),
        patch("dot.__main__._init_database"),
        patch("dot.__main__.create_task") as mock_create,
        patch("dot.__main__.console"),
    ):
        # Setup
        task = Task(
            id=uuid4(),
            title="Test Task",
            description="Test Description",
            status=TaskStatus.TODO,
            created_at=MagicMock(),
            updated_at=MagicMock(),
        )
        mock_create.return_value = task
        mock_get_session.return_value = iter([mock_session])

        # Import and run command
        from dot.__main__ import task_app

        # Run the create command
        with pytest.raises(SystemExit) as exc_info:
            task_app(["create", "Test Task", "--description", "Test Description"])

        # Assertions
        assert exc_info.value.code == 0  # type: ignore[unresolved-attribute]
        mock_create.assert_called_once_with("Test Task", "Test Description")


def test_task_create_validation_error(mock_settings):
    """Test task creation with validation error."""
    with (
        patch("dot.__main__.Settings", return_value=mock_settings),
        patch("dot.__main__._init_database"),
        patch("dot.__main__.create_task") as mock_create,
        patch("dot.__main__.console") as mock_console,
    ):
        # Setup - create_task raises ValueError
        mock_create.side_effect = ValueError("Title cannot be empty")

        # Import and run command
        from dot.__main__ import task_app

        # Run the create command
        with pytest.raises(SystemExit) as exc_info:
            task_app(["create", ""])

        # Assertions
        assert exc_info.value.code == 1  # type: ignore[unresolved-attribute]
        mock_console.print.assert_called_with(
            "✗ Error: Title cannot be empty", style="red"
        )


def test_task_list_empty(mock_settings, mock_session, mock_repository):
    """Test listing tasks when none exist."""
    with (
        patch("dot.__main__.Settings", return_value=mock_settings),
        patch("dot.__main__.get_session") as mock_get_session,
        patch("dot.__main__.SQLAlchemyTaskRepository", return_value=mock_repository),
        patch("dot.__main__._init_database"),
        patch("dot.__main__.console") as mock_console,
    ):
        # Setup - no tasks
        mock_repository.list.return_value = []
        mock_get_session.return_value = iter([mock_session])

        # Import and run command
        from dot.__main__ import task_app

        # Run the list command
        with pytest.raises(SystemExit) as exc_info:
            task_app(["list"])

        # Assertions
        assert exc_info.value.code == 0  # type: ignore[unresolved-attribute]
        mock_console.print.assert_called_with("No tasks found.")


def test_task_list_with_tasks(mock_settings, mock_session, mock_repository):
    """Test listing tasks when some exist."""
    with (
        patch("dot.__main__.Settings", return_value=mock_settings),
        patch("dot.__main__.get_session") as mock_get_session,
        patch("dot.__main__.SQLAlchemyTaskRepository", return_value=mock_repository),
        patch("dot.__main__._init_database"),
        patch("dot.__main__.console"),
    ):
        # Setup - create sample tasks
        from datetime import datetime

        tasks = [
            Task(
                id=uuid4(),
                title="Task 1",
                description=None,
                status=TaskStatus.TODO,
                created_at=datetime(2025, 11, 17, 10, 30),
                updated_at=datetime(2025, 11, 17, 10, 30),
            ),
            Task(
                id=uuid4(),
                title="Task 2",
                description=None,
                status=TaskStatus.DONE,
                created_at=datetime(2025, 11, 17, 11, 0),
                updated_at=datetime(2025, 11, 17, 11, 0),
            ),
        ]
        mock_repository.list.return_value = tasks
        mock_get_session.return_value = iter([mock_session])

        # Import and run command
        from dot.__main__ import task_app

        # Run the list command
        with pytest.raises(SystemExit) as exc_info:
            task_app(["list"])

        # Assertions
        assert exc_info.value.code == 0  # type: ignore[unresolved-attribute]
        mock_repository.list.assert_called_once_with(None)


def test_task_list_with_status_filter(mock_settings, mock_session, mock_repository):
    """Test listing tasks filtered by status."""
    with (
        patch("dot.__main__.Settings", return_value=mock_settings),
        patch("dot.__main__.get_session") as mock_get_session,
        patch("dot.__main__.SQLAlchemyTaskRepository", return_value=mock_repository),
        patch("dot.__main__._init_database"),
        patch("dot.__main__.console"),
    ):
        # Setup
        mock_repository.list.return_value = []
        mock_get_session.return_value = iter([mock_session])

        # Import and run command
        from dot.__main__ import task_app

        # Run the list command with status filter
        with pytest.raises(SystemExit):
            task_app(["list", "--status", "TODO"])

        # Assertions
        mock_repository.list.assert_called_once_with(TaskStatus.TODO)


def test_task_list_invalid_status(mock_settings):
    """Test listing tasks with invalid status."""
    with (
        patch("dot.__main__.Settings", return_value=mock_settings),
        patch("dot.__main__._init_database"),
        patch("dot.__main__.console") as mock_console,
    ):
        # Import and run command
        from dot.__main__ import task_app

        # Run the list command with invalid status
        with pytest.raises(SystemExit) as exc_info:
            task_app(["list", "--status", "INVALID"])

        # Assertions
        assert exc_info.value.code == 1  # type: ignore[unresolved-attribute]
        mock_console.print.assert_called_with(
            "✗ Error: Invalid status 'INVALID'. Must be TODO, DONE, or CANCELLED",
            style="red",
        )


def test_task_done_success(mock_settings, mock_session, mock_repository):
    """Test marking a task as done."""
    with (
        patch("dot.__main__.Settings", return_value=mock_settings),
        patch("dot.__main__.get_session") as mock_get_session,
        patch("dot.__main__.SQLAlchemyTaskRepository", return_value=mock_repository),
        patch("dot.__main__._init_database"),
        patch("dot.__main__.mark_done") as mock_mark_done,
        patch("dot.__main__.console") as mock_console,
    ):
        # Setup
        from datetime import datetime

        task = Task(
            id=uuid4(),
            title="Test Task",
            description=None,
            status=TaskStatus.TODO,
            created_at=datetime(2025, 11, 17, 10, 30),
            updated_at=datetime(2025, 11, 17, 10, 30),
        )
        done_task = Task(
            id=task.id,
            title="Test Task",
            description=None,
            status=TaskStatus.DONE,
            created_at=datetime(2025, 11, 17, 10, 30),
            updated_at=datetime(2025, 11, 17, 12, 0),
        )
        mock_repository.get.return_value = task
        mock_mark_done.return_value = done_task
        mock_get_session.return_value = iter([mock_session])

        # Import and run command
        from dot.__main__ import task_app

        # Run the done command
        task_id = str(task.id)
        with pytest.raises(SystemExit) as exc_info:
            task_app(["done", task_id])

        # Assertions
        assert exc_info.value.code == 0  # type: ignore[unresolved-attribute]
        mock_repository.update.assert_called_once()
        mock_console.print.assert_called_with(
            "✓ Task marked as DONE: Test Task", style="green"
        )


def test_task_done_with_short_id(mock_settings, mock_session, mock_repository):
    """Test marking a task as done using short ID."""
    with (
        patch("dot.__main__.Settings", return_value=mock_settings),
        patch("dot.__main__.get_session") as mock_get_session,
        patch("dot.__main__.SQLAlchemyTaskRepository", return_value=mock_repository),
        patch("dot.__main__._init_database"),
        patch("dot.__main__.mark_done") as mock_mark_done,
        patch("dot.__main__.console"),
    ):
        # Setup
        from datetime import datetime

        task_id = uuid4()
        task = Task(
            id=task_id,
            title="Test Task",
            description=None,
            status=TaskStatus.TODO,
            created_at=datetime(2025, 11, 17, 10, 30),
            updated_at=datetime(2025, 11, 17, 10, 30),
        )
        done_task = Task(
            id=task_id,
            title="Test Task",
            description=None,
            status=TaskStatus.DONE,
            created_at=datetime(2025, 11, 17, 10, 30),
            updated_at=datetime(2025, 11, 17, 12, 0),
        )
        # get() returns None for short ID
        mock_repository.get.return_value = None
        # list() returns all tasks for short ID matching
        mock_repository.list.return_value = [task]
        mock_mark_done.return_value = done_task
        mock_get_session.return_value = iter([mock_session])

        # Import and run command
        from dot.__main__ import task_app

        # Run the done command with short ID
        short_id = str(task_id)[:8]
        with pytest.raises(SystemExit) as exc_info:
            task_app(["done", short_id])

        # Assertions
        assert exc_info.value.code == 0  # type: ignore[unresolved-attribute]
        mock_repository.update.assert_called_once()


def test_task_done_not_found(mock_settings, mock_session, mock_repository):
    """Test marking a non-existent task as done."""
    with (
        patch("dot.__main__.Settings", return_value=mock_settings),
        patch("dot.__main__.get_session") as mock_get_session,
        patch("dot.__main__.SQLAlchemyTaskRepository", return_value=mock_repository),
        patch("dot.__main__._init_database"),
        patch("dot.__main__.console") as mock_console,
    ):
        # Setup
        str(uuid4())
        mock_repository.get.return_value = None
        mock_repository.list.return_value = []
        mock_get_session.return_value = iter([mock_session])

        # Import and run command
        from dot.__main__ import task_app

        # Run the done command
        with pytest.raises(SystemExit) as exc_info:
            task_app(["done", "nonexist"])

        # Assertions
        assert exc_info.value.code == 1  # type: ignore[unresolved-attribute]
        mock_console.print.assert_called_with(
            "✗ Error: Task not found: nonexist", style="red"
        )


def test_task_cancel_success(mock_settings, mock_session, mock_repository):
    """Test marking a task as cancelled."""
    with (
        patch("dot.__main__.Settings", return_value=mock_settings),
        patch("dot.__main__.get_session") as mock_get_session,
        patch("dot.__main__.SQLAlchemyTaskRepository", return_value=mock_repository),
        patch("dot.__main__._init_database"),
        patch("dot.__main__.mark_cancelled") as mock_mark_cancelled,
        patch("dot.__main__.console") as mock_console,
    ):
        # Setup
        from datetime import datetime

        task = Task(
            id=uuid4(),
            title="Test Task",
            description=None,
            status=TaskStatus.TODO,
            created_at=datetime(2025, 11, 17, 10, 30),
            updated_at=datetime(2025, 11, 17, 10, 30),
        )
        cancelled_task = Task(
            id=task.id,
            title="Test Task",
            description=None,
            status=TaskStatus.CANCELLED,
            created_at=datetime(2025, 11, 17, 10, 30),
            updated_at=datetime(2025, 11, 17, 12, 0),
        )
        mock_repository.get.return_value = task
        mock_mark_cancelled.return_value = cancelled_task
        mock_get_session.return_value = iter([mock_session])

        # Import and run command
        from dot.__main__ import task_app

        # Run the cancel command
        task_id = str(task.id)
        with pytest.raises(SystemExit) as exc_info:
            task_app(["cancel", task_id])

        # Assertions
        assert exc_info.value.code == 0  # type: ignore[unresolved-attribute]
        mock_repository.update.assert_called_once()
        mock_console.print.assert_called_with(
            "✓ Task marked as CANCELLED: Test Task", style="green"
        )


def test_task_cancel_not_found(mock_settings, mock_session, mock_repository):
    """Test cancelling a non-existent task."""
    with (
        patch("dot.__main__.Settings", return_value=mock_settings),
        patch("dot.__main__.get_session") as mock_get_session,
        patch("dot.__main__.SQLAlchemyTaskRepository", return_value=mock_repository),
        patch("dot.__main__._init_database"),
        patch("dot.__main__.console") as mock_console,
    ):
        # Setup
        mock_repository.get.return_value = None
        mock_repository.list.return_value = []
        mock_get_session.return_value = iter([mock_session])

        # Import and run command
        from dot.__main__ import task_app

        # Run the cancel command
        with pytest.raises(SystemExit) as exc_info:
            task_app(["cancel", "nonexist"])

        # Assertions
        assert exc_info.value.code == 1  # type: ignore[unresolved-attribute]
        mock_console.print.assert_called_with(
            "✗ Error: Task not found: nonexist", style="red"
        )


def test_task_done_ambiguous_id(mock_settings, mock_session, mock_repository):
    """Test marking a task as done with ambiguous short ID."""
    with (
        patch("dot.__main__.Settings", return_value=mock_settings),
        patch("dot.__main__.get_session") as mock_get_session,
        patch("dot.__main__.SQLAlchemyTaskRepository", return_value=mock_repository),
        patch("dot.__main__._init_database"),
        patch("dot.__main__.console") as mock_console,
    ):
        # Setup - create two tasks with IDs starting with same prefix "abc"
        from datetime import datetime
        from uuid import UUID

        # Create UUIDs that start with same prefix
        task1_id = UUID("abc12345-1234-1234-1234-123456789012")
        task2_id = UUID("abc98765-5678-5678-5678-567890123456")
        tasks = [
            Task(
                id=task1_id,
                title="Task 1",
                description=None,
                status=TaskStatus.TODO,
                created_at=datetime(2025, 11, 17, 10, 30),
                updated_at=datetime(2025, 11, 17, 10, 30),
            ),
            Task(
                id=task2_id,
                title="Task 2",
                description=None,
                status=TaskStatus.TODO,
                created_at=datetime(2025, 11, 17, 11, 0),
                updated_at=datetime(2025, 11, 17, 11, 0),
            ),
        ]
        mock_repository.get.return_value = None
        mock_repository.list.return_value = tasks
        mock_get_session.return_value = iter([mock_session])

        # Import and run command
        from dot.__main__ import task_app

        # Run the done command with ambiguous ID prefix
        common_prefix = "abc"

        with pytest.raises(SystemExit) as exc_info:
            task_app(["done", common_prefix])

        # Assertions
        assert exc_info.value.code == 1  # type: ignore[unresolved-attribute]
        # Check that an ambiguous ID error was printed
        calls = [str(call) for call in mock_console.print.call_args_list]
        assert any("Ambiguous ID" in str(call) for call in calls)


# Event Command Tests


def test_event_create_success(mock_settings, mock_session):
    """Test creating an event successfully."""
    from dot.domain.models import Event

    mock_event_repository = MagicMock()

    with (
        patch("dot.__main__.Settings", return_value=mock_settings),
        patch("dot.__main__.get_session") as mock_get_session,
        patch(
            "dot.repository.sqlalchemy.SQLAlchemyEventRepository",
            return_value=mock_event_repository,
        ),
        patch("dot.__main__._init_database"),
        patch("dot.domain.operations.create_event") as mock_create,
        patch("dot.__main__.console") as mock_console,
    ):
        # Setup
        from datetime import datetime

        event = Event(
            id=uuid4(),
            title="Team Meeting",
            description=None,
            occurred_at=datetime(2025, 11, 18, 14, 30),
            created_at=datetime(2025, 11, 18, 10, 0),
        )
        mock_create.return_value = event
        mock_get_session.return_value = iter([mock_session])

        # Import and run command
        from dot.__main__ import event_app

        # Run the create command
        with pytest.raises(SystemExit) as exc_info:
            event_app(["create", "Team Meeting"])

        # Assertions
        assert exc_info.value.code == 0  # type: ignore[unresolved-attribute]
        mock_create.assert_called_once()
        mock_event_repository.add.assert_called_once()
        mock_console.print.assert_any_call(
            "✓ Event created: Team Meeting", style="green"
        )


def test_event_create_with_description(mock_settings, mock_session):
    """Test creating an event with a description."""
    from dot.domain.models import Event

    mock_event_repository = MagicMock()

    with (
        patch("dot.__main__.Settings", return_value=mock_settings),
        patch("dot.__main__.get_session") as mock_get_session,
        patch(
            "dot.repository.sqlalchemy.SQLAlchemyEventRepository",
            return_value=mock_event_repository,
        ),
        patch("dot.__main__._init_database"),
        patch("dot.domain.operations.create_event") as mock_create,
        patch("dot.__main__.console"),
    ):
        # Setup
        from datetime import datetime

        event = Event(
            id=uuid4(),
            title="Team Meeting",
            description="Discuss Q4 goals",
            occurred_at=datetime(2025, 11, 18, 14, 30),
            created_at=datetime(2025, 11, 18, 10, 0),
        )
        mock_create.return_value = event
        mock_get_session.return_value = iter([mock_session])

        # Import and run command
        from dot.__main__ import event_app

        # Run the create command with description
        with pytest.raises(SystemExit) as exc_info:
            event_app(["create", "Team Meeting", "--description", "Discuss Q4 goals"])

        # Assertions
        assert exc_info.value.code == 0  # type: ignore[unresolved-attribute]
        mock_create.assert_called_once()


def test_event_create_with_date(mock_settings, mock_session):
    """Test creating an event with a specific date."""
    from dot.domain.models import Event

    mock_event_repository = MagicMock()

    with (
        patch("dot.__main__.Settings", return_value=mock_settings),
        patch("dot.__main__.get_session") as mock_get_session,
        patch(
            "dot.repository.sqlalchemy.SQLAlchemyEventRepository",
            return_value=mock_event_repository,
        ),
        patch("dot.__main__._init_database"),
        patch("dot.domain.operations.create_event") as mock_create,
        patch("dot.__main__.console"),
    ):
        # Setup
        from datetime import datetime

        event = Event(
            id=uuid4(),
            title="Team Meeting",
            description=None,
            occurred_at=datetime(2025, 12, 1, 0, 0),
            created_at=datetime(2025, 11, 18, 10, 0),
        )
        mock_create.return_value = event
        mock_get_session.return_value = iter([mock_session])

        # Import and run command
        from dot.__main__ import event_app

        # Run the create command with date (YYYY-MM-DD format)
        with pytest.raises(SystemExit) as exc_info:
            event_app(["create", "Team Meeting", "--date", "2025-12-01"])

        # Assertions
        assert exc_info.value.code == 0  # type: ignore[unresolved-attribute]
        mock_create.assert_called_once()


def test_event_create_validation_error(mock_settings):
    """Test event creation with validation error."""
    with (
        patch("dot.__main__.Settings", return_value=mock_settings),
        patch("dot.__main__._init_database"),
        patch("dot.domain.operations.create_event") as mock_create,
        patch("dot.__main__.console") as mock_console,
    ):
        # Setup - create_event raises ValueError
        mock_create.side_effect = ValueError("Title cannot be empty")

        # Import and run command
        from dot.__main__ import event_app

        # Run the create command
        with pytest.raises(SystemExit) as exc_info:
            event_app(["create", ""])

        # Assertions
        assert exc_info.value.code == 1  # type: ignore[unresolved-attribute]
        mock_console.print.assert_called_with(
            "✗ Error: Title cannot be empty", style="red"
        )


def test_event_list_empty(mock_settings, mock_session):
    """Test listing events when none exist."""
    mock_event_repository = MagicMock()

    with (
        patch("dot.__main__.Settings", return_value=mock_settings),
        patch("dot.__main__.get_session") as mock_get_session,
        patch(
            "dot.repository.sqlalchemy.SQLAlchemyEventRepository",
            return_value=mock_event_repository,
        ),
        patch("dot.__main__._init_database"),
        patch("dot.__main__.console") as mock_console,
    ):
        # Setup - no events
        mock_event_repository.list.return_value = []
        mock_get_session.return_value = iter([mock_session])

        # Import and run command
        from dot.__main__ import event_app

        # Run the list command
        with pytest.raises(SystemExit) as exc_info:
            event_app(["list"])

        # Assertions
        assert exc_info.value.code == 0  # type: ignore[unresolved-attribute]
        mock_console.print.assert_called_with("No events found.")


def test_event_list_with_events(mock_settings, mock_session):
    """Test listing events when some exist."""
    from dot.domain.models import Event

    mock_event_repository = MagicMock()

    with (
        patch("dot.__main__.Settings", return_value=mock_settings),
        patch("dot.__main__.get_session") as mock_get_session,
        patch(
            "dot.repository.sqlalchemy.SQLAlchemyEventRepository",
            return_value=mock_event_repository,
        ),
        patch("dot.__main__._init_database"),
        patch("dot.__main__.console"),
    ):
        # Setup - create sample events
        from datetime import datetime

        events = [
            Event(
                id=uuid4(),
                title="Event 1",
                description=None,
                occurred_at=datetime(2025, 11, 17, 10, 30),
                created_at=datetime(2025, 11, 17, 10, 30),
            ),
            Event(
                id=uuid4(),
                title="Event 2",
                description=None,
                occurred_at=datetime(2025, 11, 18, 11, 0),
                created_at=datetime(2025, 11, 18, 11, 0),
            ),
        ]
        mock_event_repository.list.return_value = events
        mock_get_session.return_value = iter([mock_session])

        # Import and run command
        from dot.__main__ import event_app

        # Run the list command
        with pytest.raises(SystemExit) as exc_info:
            event_app(["list"])

        # Assertions
        assert exc_info.value.code == 0  # type: ignore[unresolved-attribute]
        mock_event_repository.list.assert_called_once()


def test_event_list_by_date(mock_settings, mock_session):
    """Test listing events filtered by date."""
    mock_event_repository = MagicMock()

    with (
        patch("dot.__main__.Settings", return_value=mock_settings),
        patch("dot.__main__.get_session") as mock_get_session,
        patch(
            "dot.repository.sqlalchemy.SQLAlchemyEventRepository",
            return_value=mock_event_repository,
        ),
        patch("dot.__main__._init_database"),
        patch("dot.__main__.console"),
    ):
        # Setup
        mock_event_repository.list_by_date.return_value = []
        mock_get_session.return_value = iter([mock_session])

        # Import and run command
        from dot.__main__ import event_app

        # Run the list command with date filter
        with pytest.raises(SystemExit):
            event_app(["list", "--date", "2025-11-18"])

        # Assertions
        mock_event_repository.list_by_date.assert_called_once()


def test_event_list_by_range(mock_settings, mock_session):
    """Test listing events filtered by date range."""
    mock_event_repository = MagicMock()

    with (
        patch("dot.__main__.Settings", return_value=mock_settings),
        patch("dot.__main__.get_session") as mock_get_session,
        patch(
            "dot.repository.sqlalchemy.SQLAlchemyEventRepository",
            return_value=mock_event_repository,
        ),
        patch("dot.__main__._init_database"),
        patch("dot.__main__.console"),
    ):
        # Setup
        mock_event_repository.list_by_range.return_value = []
        mock_get_session.return_value = iter([mock_session])

        # Import and run command
        from dot.__main__ import event_app

        # Run the list command with range filter (colon-separated format)
        with pytest.raises(SystemExit):
            event_app(["list", "--range", "2025-11-01:2025-11-30"])

        # Assertions
        mock_event_repository.list_by_range.assert_called_once()


def test_event_list_invalid_date_format(mock_settings):
    """Test listing events with invalid date format."""
    with (
        patch("dot.__main__.Settings", return_value=mock_settings),
        patch("dot.__main__._init_database"),
        patch("dot.__main__.console") as mock_console,
    ):
        # Import and run command
        from dot.__main__ import event_app

        # Run the list command with invalid date
        with pytest.raises(SystemExit) as exc_info:
            event_app(["list", "--date", "invalid-date"])

        # Assertions
        assert exc_info.value.code == 1  # type: ignore[unresolved-attribute]
        # Check that an error was printed
        calls = [str(call) for call in mock_console.print.call_args_list]
        assert any("Error" in str(call) for call in calls)


# Note Command Tests


def test_note_create_success(mock_settings, mock_session):
    """Test creating a note successfully."""
    from dot.domain.models import Note

    mock_note_repository = MagicMock()

    with (
        patch("dot.__main__.Settings", return_value=mock_settings),
        patch("dot.__main__.get_session") as mock_get_session,
        patch(
            "dot.repository.sqlalchemy.SQLAlchemyNoteRepository",
            return_value=mock_note_repository,
        ),
        patch("dot.__main__._init_database"),
        patch("dot.domain.operations.create_note") as mock_create,
        patch("dot.__main__.console") as mock_console,
    ):
        # Setup
        from datetime import datetime

        note = Note(
            id=uuid4(),
            title="Meeting Notes",
            content="Discussed project timeline",
            created_at=datetime(2025, 11, 18, 10, 0),
        )
        mock_create.return_value = note
        mock_get_session.return_value = iter([mock_session])

        # Import and run command
        from dot.__main__ import note_app

        # Run the create command
        with pytest.raises(SystemExit) as exc_info:
            note_app(["create", "Meeting Notes", "Discussed project timeline"])

        # Assertions
        assert exc_info.value.code == 0  # type: ignore[unresolved-attribute]
        mock_create.assert_called_once_with(
            "Meeting Notes", "Discussed project timeline"
        )
        mock_note_repository.add.assert_called_once()
        mock_console.print.assert_any_call(
            "✓ Note created: Meeting Notes", style="green"
        )


def test_note_create_validation_error(mock_settings):
    """Test note creation with validation error."""
    with (
        patch("dot.__main__.Settings", return_value=mock_settings),
        patch("dot.__main__._init_database"),
        patch("dot.domain.operations.create_note") as mock_create,
        patch("dot.__main__.console") as mock_console,
    ):
        # Setup - create_note raises ValueError
        mock_create.side_effect = ValueError("Content cannot be empty")

        # Import and run command
        from dot.__main__ import note_app

        # Run the create command
        with pytest.raises(SystemExit) as exc_info:
            note_app(["create", "Title", ""])

        # Assertions
        assert exc_info.value.code == 1  # type: ignore[unresolved-attribute]
        mock_console.print.assert_called_with(
            "✗ Error: Content cannot be empty", style="red"
        )


def test_note_list_empty(mock_settings, mock_session):
    """Test listing notes when none exist."""
    mock_note_repository = MagicMock()

    with (
        patch("dot.__main__.Settings", return_value=mock_settings),
        patch("dot.__main__.get_session") as mock_get_session,
        patch(
            "dot.repository.sqlalchemy.SQLAlchemyNoteRepository",
            return_value=mock_note_repository,
        ),
        patch("dot.__main__._init_database"),
        patch("dot.__main__.console") as mock_console,
    ):
        # Setup - no notes
        mock_note_repository.list.return_value = []
        mock_get_session.return_value = iter([mock_session])

        # Import and run command
        from dot.__main__ import note_app

        # Run the list command
        with pytest.raises(SystemExit) as exc_info:
            note_app(["list"])

        # Assertions
        assert exc_info.value.code == 0  # type: ignore[unresolved-attribute]
        mock_console.print.assert_called_with("No notes found.")


def test_note_list_with_notes(mock_settings, mock_session):
    """Test listing notes when some exist."""
    from dot.domain.models import Note

    mock_note_repository = MagicMock()

    with (
        patch("dot.__main__.Settings", return_value=mock_settings),
        patch("dot.__main__.get_session") as mock_get_session,
        patch(
            "dot.repository.sqlalchemy.SQLAlchemyNoteRepository",
            return_value=mock_note_repository,
        ),
        patch("dot.__main__._init_database"),
        patch("dot.__main__.console"),
    ):
        # Setup - create sample notes
        from datetime import datetime

        notes = [
            Note(
                id=uuid4(),
                title="Note 1",
                content="Content 1",
                created_at=datetime(2025, 11, 17, 10, 30),
            ),
            Note(
                id=uuid4(),
                title="Note 2",
                content="Content 2",
                created_at=datetime(2025, 11, 18, 11, 0),
            ),
        ]
        mock_note_repository.list.return_value = notes
        mock_get_session.return_value = iter([mock_session])

        # Import and run command
        from dot.__main__ import note_app

        # Run the list command
        with pytest.raises(SystemExit) as exc_info:
            note_app(["list"])

        # Assertions
        assert exc_info.value.code == 0  # type: ignore[unresolved-attribute]
        mock_note_repository.list.assert_called_once()


def test_note_show_success(mock_settings, mock_session):
    """Test showing a note by ID."""
    from dot.domain.models import Note

    mock_note_repository = MagicMock()

    with (
        patch("dot.__main__.Settings", return_value=mock_settings),
        patch("dot.__main__.get_session") as mock_get_session,
        patch(
            "dot.repository.sqlalchemy.SQLAlchemyNoteRepository",
            return_value=mock_note_repository,
        ),
        patch("dot.__main__._init_database"),
        patch("dot.__main__.console") as mock_console,
    ):
        # Setup
        from datetime import datetime

        note_id = uuid4()
        note = Note(
            id=note_id,
            title="Meeting Notes",
            content="Discussed project timeline",
            created_at=datetime(2025, 11, 18, 10, 0),
        )
        mock_note_repository.get.return_value = note
        mock_get_session.return_value = iter([mock_session])

        # Import and run command
        from dot.__main__ import note_app

        # Run the show command
        with pytest.raises(SystemExit) as exc_info:
            note_app(["show", str(note_id)])

        # Assertions
        assert exc_info.value.code == 0  # type: ignore[unresolved-attribute]
        mock_note_repository.get.assert_called_once_with(note_id)
        mock_console.print.assert_called_once()


def test_note_show_with_short_id(mock_settings, mock_session):
    """Test showing a note using short ID."""
    from dot.domain.models import Note

    mock_note_repository = MagicMock()

    with (
        patch("dot.__main__.Settings", return_value=mock_settings),
        patch("dot.__main__.get_session") as mock_get_session,
        patch(
            "dot.repository.sqlalchemy.SQLAlchemyNoteRepository",
            return_value=mock_note_repository,
        ),
        patch("dot.__main__._init_database"),
        patch("dot.__main__.console"),
    ):
        # Setup
        from datetime import datetime

        note_id = uuid4()
        note = Note(
            id=note_id,
            title="Meeting Notes",
            content="Discussed project timeline",
            created_at=datetime(2025, 11, 18, 10, 0),
        )
        # get() returns None for short ID
        mock_note_repository.get.return_value = None
        # list() returns all notes for short ID matching
        mock_note_repository.list.return_value = [note]
        mock_get_session.return_value = iter([mock_session])

        # Import and run command
        from dot.__main__ import note_app

        # Run the show command with short ID
        short_id = str(note_id)[:8]
        with pytest.raises(SystemExit) as exc_info:
            note_app(["show", short_id])

        # Assertions
        assert exc_info.value.code == 0  # type: ignore[unresolved-attribute]


def test_note_show_not_found(mock_settings, mock_session):
    """Test showing a non-existent note."""
    mock_note_repository = MagicMock()

    with (
        patch("dot.__main__.Settings", return_value=mock_settings),
        patch("dot.__main__.get_session") as mock_get_session,
        patch(
            "dot.repository.sqlalchemy.SQLAlchemyNoteRepository",
            return_value=mock_note_repository,
        ),
        patch("dot.__main__._init_database"),
        patch("dot.__main__.console") as mock_console,
    ):
        # Setup
        mock_note_repository.get.return_value = None
        mock_note_repository.list.return_value = []
        mock_get_session.return_value = iter([mock_session])

        # Import and run command
        from dot.__main__ import note_app

        # Run the show command
        with pytest.raises(SystemExit) as exc_info:
            note_app(["show", "nonexistent"])

        # Assertions
        assert exc_info.value.code == 1  # type: ignore[unresolved-attribute]
        mock_console.print.assert_called_with(
            "✗ Error: Note not found: nonexistent", style="red"
        )


def test_note_show_ambiguous_id(mock_settings, mock_session):
    """Test showing a note with ambiguous short ID."""
    from dot.domain.models import Note
    from uuid import UUID

    mock_note_repository = MagicMock()

    with (
        patch("dot.__main__.Settings", return_value=mock_settings),
        patch("dot.__main__.get_session") as mock_get_session,
        patch(
            "dot.repository.sqlalchemy.SQLAlchemyNoteRepository",
            return_value=mock_note_repository,
        ),
        patch("dot.__main__._init_database"),
        patch("dot.__main__.console") as mock_console,
    ):
        # Setup - create two notes with IDs starting with same prefix
        from datetime import datetime

        note1_id = UUID("abc12345-1234-1234-1234-123456789012")
        note2_id = UUID("abc98765-5678-5678-5678-567890123456")
        notes = [
            Note(
                id=note1_id,
                title="Note 1",
                content="Content 1",
                created_at=datetime(2025, 11, 18, 10, 0),
            ),
            Note(
                id=note2_id,
                title="Note 2",
                content="Content 2",
                created_at=datetime(2025, 11, 18, 11, 0),
            ),
        ]
        mock_note_repository.get.return_value = None
        mock_note_repository.list.return_value = notes
        mock_get_session.return_value = iter([mock_session])

        # Import and run command
        from dot.__main__ import note_app

        # Run the show command with ambiguous ID prefix
        common_prefix = "abc"

        with pytest.raises(SystemExit) as exc_info:
            note_app(["show", common_prefix])

        # Assertions
        assert exc_info.value.code == 1  # type: ignore[unresolved-attribute]
        # Check that an ambiguous ID error was printed
        calls = [str(call) for call in mock_console.print.call_args_list]
        assert any("Ambiguous ID" in str(call) for call in calls)


# Log Command Tests


@patch("dot.__main__.console")
@patch("dot.__main__.get_session")
@patch("dot.__main__._init_database")
@patch("dot.__main__.Settings")
def test_log_for_today(
    mock_settings_class, mock_init_db, mock_get_session, mock_console
):
    """Test viewing daily log for today."""

    from dot.domain.operations import create_event, create_note, create_task
    from dot.repository.memory import (
        InMemoryEventRepository,
        InMemoryNoteRepository,
        InMemoryTaskRepository,
    )

    # Setup mocks
    mock_settings = MagicMock()
    mock_settings.db_path = Path("/tmp/test.db")
    mock_settings_class.return_value = mock_settings

    mock_session = MagicMock()

    # Create in-memory repositories
    task_repo = InMemoryTaskRepository()
    event_repo = InMemoryEventRepository()
    note_repo = InMemoryNoteRepository()

    # Add test items
    task = create_task("Buy groceries")
    event = create_event("Team meeting")
    note = create_note("Meeting notes", "Important discussion")

    task_repo.add(task)
    event_repo.add(event)
    note_repo.add(note)

    # Mock repository creation
    with (
        patch("dot.__main__.SQLAlchemyTaskRepository", return_value=task_repo),
        patch("dot.__main__.SQLAlchemyEventRepository", return_value=event_repo),
        patch("dot.__main__.SQLAlchemyNoteRepository", return_value=note_repo),
    ):
        mock_get_session.return_value = iter([mock_session])

        # Import and run command
        from dot.__main__ import log

        # Run the log command for today
        with pytest.raises(SystemExit) as exc_info:
            log(None)

        # Assertions
        assert exc_info.value.code == 0  # type: ignore[unresolved-attribute]
        # Verify output contains daily log header
        calls = [str(call) for call in mock_console.print.call_args_list]
        assert any("Daily Log" in str(call) for call in calls)
        assert any("Tasks" in str(call) for call in calls)
        assert any("Events" in str(call) for call in calls)
        assert any("Notes" in str(call) for call in calls)


@patch("dot.__main__.console")
@patch("dot.__main__.get_session")
@patch("dot.__main__._init_database")
@patch("dot.__main__.Settings")
def test_log_for_specific_date(
    mock_settings_class, mock_init_db, mock_get_session, mock_console
):
    """Test viewing daily log for a specific date."""

    from dot.repository.memory import (
        InMemoryEventRepository,
        InMemoryNoteRepository,
        InMemoryTaskRepository,
    )

    # Setup mocks
    mock_settings = MagicMock()
    mock_settings.db_path = Path("/tmp/test.db")
    mock_settings_class.return_value = mock_settings

    mock_session = MagicMock()

    # Create in-memory repositories
    task_repo = InMemoryTaskRepository()
    event_repo = InMemoryEventRepository()
    note_repo = InMemoryNoteRepository()

    # Mock repository creation
    with (
        patch("dot.__main__.SQLAlchemyTaskRepository", return_value=task_repo),
        patch("dot.__main__.SQLAlchemyEventRepository", return_value=event_repo),
        patch("dot.__main__.SQLAlchemyNoteRepository", return_value=note_repo),
    ):
        mock_get_session.return_value = iter([mock_session])

        # Import and run command
        from dot.__main__ import log

        # Run the log command for a specific date
        with pytest.raises(SystemExit) as exc_info:
            log("2025-11-17")

        # Assertions
        assert exc_info.value.code == 0  # type: ignore[unresolved-attribute]
        # Verify date is displayed
        calls = [str(call) for call in mock_console.print.call_args_list]
        assert any("2025-11-17" in str(call) for call in calls)


@patch("dot.__main__.console")
@patch("dot.__main__.get_session")
@patch("dot.__main__._init_database")
@patch("dot.__main__.Settings")
def test_log_empty_date(
    mock_settings_class, mock_init_db, mock_get_session, mock_console
):
    """Test viewing daily log for a date with no items."""
    from dot.repository.memory import (
        InMemoryEventRepository,
        InMemoryNoteRepository,
        InMemoryTaskRepository,
    )

    # Setup mocks
    mock_settings = MagicMock()
    mock_settings.db_path = Path("/tmp/test.db")
    mock_settings_class.return_value = mock_settings

    mock_session = MagicMock()

    # Create empty in-memory repositories
    task_repo = InMemoryTaskRepository()
    event_repo = InMemoryEventRepository()
    note_repo = InMemoryNoteRepository()

    # Mock repository creation
    with (
        patch("dot.__main__.SQLAlchemyTaskRepository", return_value=task_repo),
        patch("dot.__main__.SQLAlchemyEventRepository", return_value=event_repo),
        patch("dot.__main__.SQLAlchemyNoteRepository", return_value=note_repo),
    ):
        mock_get_session.return_value = iter([mock_session])

        # Import and run command
        from dot.__main__ import log

        # Run the log command for today (which has no items)
        with pytest.raises(SystemExit) as exc_info:
            log(None)

        # Assertions
        assert exc_info.value.code == 0  # type: ignore[unresolved-attribute]
        # Verify message for no entries
        calls = [str(call) for call in mock_console.print.call_args_list]
        assert any("No entries for this date" in str(call) for call in calls)


@patch("dot.__main__.console")
def test_log_invalid_date_format(mock_console):
    """Test log command with invalid date format."""
    from dot.__main__ import log

    # Run with invalid date
    with pytest.raises(SystemExit) as exc_info:
        log("invalid-date")

    # Assertions
    assert exc_info.value.code == 1  # type: ignore[unresolved-attribute]
    # Check for error message
    calls = [str(call) for call in mock_console.print.call_args_list]
    assert any("Invalid date format" in str(call) for call in calls)
