"""Contract tests for repository interfaces.

These tests ensure that all repository implementations (in-memory, SQLAlchemy)
behave identically according to the repository contract.
"""

from datetime import UTC, date, datetime, timedelta
from uuid import uuid4


from dot.domain.models import Task, TaskStatus
from dot.repository.abstract import TaskRepository


def test_task_repository_add_and_get(task_repository: TaskRepository) -> None:
    """Test adding and retrieving a task."""
    task = Task(
        id=uuid4(),
        title="Test task",
        description="Test description",
        status=TaskStatus.TODO,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )

    task_repository.add(task)

    retrieved = task_repository.get(task.id)
    assert retrieved is not None
    assert retrieved.id == task.id
    assert retrieved.title == task.title
    assert retrieved.description == task.description
    assert retrieved.status == task.status


def test_task_repository_get_nonexistent(task_repository: TaskRepository) -> None:
    """Test getting a task that doesn't exist."""
    result = task_repository.get(uuid4())
    assert result is None


def test_task_repository_list_empty(task_repository: TaskRepository) -> None:
    """Test listing tasks when repository is empty."""
    tasks = task_repository.list()
    assert tasks == []


def test_task_repository_list_all(task_repository: TaskRepository) -> None:
    """Test listing all tasks."""
    task1 = Task(
        id=uuid4(),
        title="Task 1",
        description=None,
        status=TaskStatus.TODO,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    task2 = Task(
        id=uuid4(),
        title="Task 2",
        description=None,
        status=TaskStatus.DONE,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )

    task_repository.add(task1)
    task_repository.add(task2)

    tasks = task_repository.list()
    assert len(tasks) == 2
    assert task1 in tasks
    assert task2 in tasks


def test_task_repository_list_by_status(task_repository: TaskRepository) -> None:
    """Test listing tasks filtered by status."""
    todo_task = Task(
        id=uuid4(),
        title="TODO Task",
        description=None,
        status=TaskStatus.TODO,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    done_task = Task(
        id=uuid4(),
        title="DONE Task",
        description=None,
        status=TaskStatus.DONE,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )

    task_repository.add(todo_task)
    task_repository.add(done_task)

    todo_tasks = task_repository.list(status=TaskStatus.TODO)
    assert len(todo_tasks) == 1
    assert todo_tasks[0].id == todo_task.id

    done_tasks = task_repository.list(status=TaskStatus.DONE)
    assert len(done_tasks) == 1
    assert done_tasks[0].id == done_task.id


def test_task_repository_update(task_repository: TaskRepository) -> None:
    """Test updating a task."""
    task = Task(
        id=uuid4(),
        title="Original",
        description=None,
        status=TaskStatus.TODO,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )

    task_repository.add(task)

    updated_task = Task(
        id=task.id,
        title="Updated",
        description="New description",
        status=TaskStatus.DONE,
        created_at=task.created_at,
        updated_at=datetime.now(UTC),
    )

    task_repository.update(updated_task)

    retrieved = task_repository.get(task.id)
    assert retrieved is not None
    assert retrieved.title == "Updated"
    assert retrieved.description == "New description"
    assert retrieved.status == TaskStatus.DONE


def test_task_repository_delete(task_repository: TaskRepository) -> None:
    """Test deleting a task."""
    task = Task(
        id=uuid4(),
        title="To Delete",
        description=None,
        status=TaskStatus.TODO,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )

    task_repository.add(task)
    assert task_repository.get(task.id) is not None

    task_repository.delete(task.id)

    assert task_repository.get(task.id) is None


def test_task_repository_list_by_date(task_repository: TaskRepository) -> None:
    """Test listing tasks created on a specific date."""
    today = datetime.now(UTC)
    yesterday = today - timedelta(days=1)

    task_today = Task(
        id=uuid4(),
        title="Today Task",
        description=None,
        status=TaskStatus.TODO,
        created_at=today,
        updated_at=today,
    )
    task_yesterday = Task(
        id=uuid4(),
        title="Yesterday Task",
        description=None,
        status=TaskStatus.TODO,
        created_at=yesterday,
        updated_at=yesterday,
    )

    task_repository.add(task_today)
    task_repository.add(task_yesterday)

    tasks_today = task_repository.list_by_date(today.date())
    assert len(tasks_today) == 1
    assert tasks_today[0].id == task_today.id

    tasks_yesterday = task_repository.list_by_date(yesterday.date())
    assert len(tasks_yesterday) == 1
    assert tasks_yesterday[0].id == task_yesterday.id


def test_task_repository_list_by_date_empty(task_repository: TaskRepository) -> None:
    """Test listing tasks for a date with no tasks."""
    future_date = date.today() + timedelta(days=365)
    tasks = task_repository.list_by_date(future_date)
    assert tasks == []


def test_task_repository_update_nonexistent(task_repository: TaskRepository) -> None:
    """Test updating a task that doesn't exist (should be a no-op)."""
    nonexistent_task = Task(
        id=uuid4(),
        title="Nonexistent",
        description=None,
        status=TaskStatus.TODO,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )

    # Update should not raise an error, just silently fail
    task_repository.update(nonexistent_task)

    # Task should still not exist
    retrieved = task_repository.get(nonexistent_task.id)
    assert retrieved is None


def test_task_repository_delete_nonexistent(task_repository: TaskRepository) -> None:
    """Test deleting a task that doesn't exist (should be a no-op)."""
    nonexistent_id = uuid4()

    # Delete should not raise an error
    task_repository.delete(nonexistent_id)

    # Verify repository is still empty
    tasks = task_repository.list()
    assert len(tasks) == 0


# Event Repository Contract Tests


def test_event_repository_add_and_get(event_repository) -> None:
    """Test adding and retrieving an event."""
    from dot.domain.models import Event

    event = Event(
        id=uuid4(),
        title="Team meeting",
        description="Discuss Q4 plans",
        occurred_at=datetime.now(UTC),
        created_at=datetime.now(UTC),
    )

    event_repository.add(event)

    retrieved = event_repository.get(event.id)
    assert retrieved is not None
    assert retrieved.id == event.id
    assert retrieved.title == event.title
    assert retrieved.description == event.description


def test_event_repository_get_nonexistent(event_repository) -> None:
    """Test getting an event that doesn't exist."""
    result = event_repository.get(uuid4())
    assert result is None


def test_event_repository_list_empty(event_repository) -> None:
    """Test listing events when repository is empty."""
    events = event_repository.list()
    assert events == []


def test_event_repository_list_all(event_repository) -> None:
    """Test listing all events."""
    from dot.domain.models import Event

    event1 = Event(
        id=uuid4(),
        title="Event 1",
        description=None,
        occurred_at=datetime.now(UTC),
        created_at=datetime.now(UTC),
    )
    event2 = Event(
        id=uuid4(),
        title="Event 2",
        description=None,
        occurred_at=datetime.now(UTC),
        created_at=datetime.now(UTC),
    )

    event_repository.add(event1)
    event_repository.add(event2)

    events = event_repository.list()
    assert len(events) == 2
    assert event1 in events
    assert event2 in events


def test_event_repository_list_by_date(event_repository) -> None:
    """Test listing events that occurred on a specific date."""
    from dot.domain.models import Event

    today = datetime.now(UTC)
    yesterday = today - timedelta(days=1)

    event_today = Event(
        id=uuid4(),
        title="Today Event",
        description=None,
        occurred_at=today,
        created_at=today,
    )
    event_yesterday = Event(
        id=uuid4(),
        title="Yesterday Event",
        description=None,
        occurred_at=yesterday,
        created_at=today,
    )

    event_repository.add(event_today)
    event_repository.add(event_yesterday)

    events_today = event_repository.list_by_date(today.date())
    assert len(events_today) == 1
    assert events_today[0].id == event_today.id

    events_yesterday = event_repository.list_by_date(yesterday.date())
    assert len(events_yesterday) == 1
    assert events_yesterday[0].id == event_yesterday.id


def test_event_repository_list_by_range(event_repository) -> None:
    """Test listing events within a date range."""
    from dot.domain.models import Event

    now = datetime.now(UTC)
    day1 = now - timedelta(days=3)
    day2 = now - timedelta(days=2)
    day3 = now - timedelta(days=1)

    event1 = Event(
        id=uuid4(),
        title="Event 1",
        description=None,
        occurred_at=day1,
        created_at=now,
    )
    event2 = Event(
        id=uuid4(),
        title="Event 2",
        description=None,
        occurred_at=day2,
        created_at=now,
    )
    event3 = Event(
        id=uuid4(),
        title="Event 3",
        description=None,
        occurred_at=day3,
        created_at=now,
    )

    event_repository.add(event1)
    event_repository.add(event2)
    event_repository.add(event3)

    # Get events from day2 to day3 (should include event2 and event3)
    events_in_range = event_repository.list_by_range(day2.date(), day3.date())
    assert len(events_in_range) == 2
    assert any(e.id == event2.id for e in events_in_range)
    assert any(e.id == event3.id for e in events_in_range)


def test_event_repository_delete(event_repository) -> None:
    """Test deleting an event."""
    from dot.domain.models import Event

    event = Event(
        id=uuid4(),
        title="To Delete",
        description=None,
        occurred_at=datetime.now(UTC),
        created_at=datetime.now(UTC),
    )

    event_repository.add(event)
    assert event_repository.get(event.id) is not None

    event_repository.delete(event.id)

    assert event_repository.get(event.id) is None


def test_event_repository_delete_nonexistent(event_repository) -> None:
    """Test deleting an event that doesn't exist (should be a no-op)."""
    nonexistent_id = uuid4()

    # Delete should not raise an error
    event_repository.delete(nonexistent_id)

    # Verify repository is still empty
    events = event_repository.list()
    assert len(events) == 0


# NoteRepository Contract Tests


def test_note_repository_add_and_get(note_repository) -> None:
    """Test adding and retrieving a note."""
    from dot.domain.models import Note

    note = Note(
        id=uuid4(),
        title="Meeting Notes",
        content="Discussed project timeline and deliverables",
        created_at=datetime.now(UTC),
    )

    note_repository.add(note)
    retrieved = note_repository.get(note.id)

    assert retrieved is not None
    assert retrieved.id == note.id
    assert retrieved.title == note.title
    assert retrieved.content == note.content


def test_note_repository_get_nonexistent(note_repository) -> None:
    """Test getting a note that doesn't exist."""
    nonexistent_id = uuid4()
    note = note_repository.get(nonexistent_id)
    assert note is None


def test_note_repository_list_empty(note_repository) -> None:
    """Test listing notes when repository is empty."""
    notes = note_repository.list()
    assert len(notes) == 0


def test_note_repository_list_all(note_repository) -> None:
    """Test listing all notes."""
    from dot.domain.models import Note

    note1 = Note(
        id=uuid4(),
        title="Note 1",
        content="Content 1",
        created_at=datetime.now(UTC),
    )
    note2 = Note(
        id=uuid4(),
        title="Note 2",
        content="Content 2",
        created_at=datetime.now(UTC),
    )

    note_repository.add(note1)
    note_repository.add(note2)

    notes = note_repository.list()
    assert len(notes) == 2
    note_ids = {n.id for n in notes}
    assert note1.id in note_ids
    assert note2.id in note_ids


def test_note_repository_list_by_date(note_repository) -> None:
    """Test listing notes created on a specific date."""
    from dot.domain.models import Note

    today = datetime.now(UTC)
    yesterday = today - timedelta(days=1)

    note_today = Note(
        id=uuid4(),
        title="Today's Note",
        content="Content",
        created_at=today,
    )
    note_yesterday = Note(
        id=uuid4(),
        title="Yesterday's Note",
        content="Content",
        created_at=yesterday,
    )

    note_repository.add(note_today)
    note_repository.add(note_yesterday)

    today_notes = note_repository.list_by_date(today.date())
    assert len(today_notes) == 1
    assert today_notes[0].id == note_today.id

    yesterday_notes = note_repository.list_by_date(yesterday.date())
    assert len(yesterday_notes) == 1
    assert yesterday_notes[0].id == note_yesterday.id


def test_note_repository_delete(note_repository) -> None:
    """Test deleting a note."""
    from dot.domain.models import Note

    note = Note(
        id=uuid4(),
        title="To Delete",
        content="Content",
        created_at=datetime.now(UTC),
    )

    note_repository.add(note)
    assert note_repository.get(note.id) is not None

    note_repository.delete(note.id)
    assert note_repository.get(note.id) is None


def test_note_repository_delete_nonexistent(note_repository) -> None:
    """Test deleting a note that doesn't exist (should be a no-op)."""
    nonexistent_id = uuid4()

    # Delete should not raise an error
    note_repository.delete(nonexistent_id)

    # Verify repository is still empty
    notes = note_repository.list()
    assert len(notes) == 0
