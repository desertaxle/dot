"""Tests for the output module."""

import io
from datetime import datetime, timezone
from uuid import uuid4

from rich.console import Console

from dot.domain.models import Event, Note, Task, TaskStatus
from dot.output import (
    build_event_detail_panel,
    build_event_tree,
    build_log_tree,
    build_note_detail_panel,
    build_note_tree,
    build_task_detail_panel,
    build_task_tree,
    custom_theme,
    print_error,
    print_success,
)


def test_print_success():
    """Test print_success outputs correctly."""
    # Capture output
    output = io.StringIO()
    test_console = Console(
        file=output, force_terminal=True, legacy_windows=False, theme=custom_theme
    )

    # Monkey patch the console in the output module
    import dot.output

    original_console = dot.output.console
    dot.output.console = test_console

    try:
        print_success("Task created successfully")
        result = output.getvalue()
        assert "Task created successfully" in result
        assert "✓" in result
    finally:
        dot.output.console = original_console


def test_print_error():
    """Test print_error outputs to stderr correctly."""
    # Capture stderr output
    output = io.StringIO()
    test_error_console = Console(
        file=output,
        force_terminal=True,
        stderr=True,
        legacy_windows=False,
        theme=custom_theme,
    )

    # Monkey patch the error_console in the output module
    import dot.output

    original_error_console = dot.output.error_console
    dot.output.error_console = test_error_console

    try:
        print_error("Task not found")
        result = output.getvalue()
        assert "Task not found" in result
        assert "✗" in result
    finally:
        dot.output.error_console = original_error_console


def test_build_task_tree_empty():
    """Test build_task_tree with no tasks."""
    tree = build_task_tree([])
    # Check that the tree has a root
    assert tree.label == "📋 [bold task]Tasks[/bold task]"
    # The tree should have a "(No tasks)" child
    assert len(tree.children) == 1


def test_build_task_tree_single_task():
    """Test build_task_tree with a single task."""
    now = datetime.now(timezone.utc)
    task = Task(
        id=uuid4(),
        title="Buy milk",
        description="Get whole milk from the store",
        status=TaskStatus.TODO,
        priority=1,
        created_at=now,
        updated_at=now,
    )

    tree = build_task_tree([task])
    assert tree.label == "📋 [bold task]Tasks[/bold task]"
    assert len(tree.children) == 1


def test_build_task_tree_multiple_tasks():
    """Test build_task_tree with multiple tasks."""
    now = datetime.now(timezone.utc)
    tasks = [
        Task(
            id=uuid4(),
            title="Task 1",
            status=TaskStatus.TODO,
            created_at=now,
            updated_at=now,
        ),
        Task(
            id=uuid4(),
            title="Task 2",
            status=TaskStatus.DONE,
            created_at=now,
            updated_at=now,
        ),
        Task(
            id=uuid4(),
            title="Task 3",
            status=TaskStatus.CANCELLED,
            created_at=now,
            updated_at=now,
        ),
    ]

    tree = build_task_tree(tasks, show_cancelled=True)
    assert tree.label == "📋 [bold task]Tasks[/bold task]"
    assert len(tree.children) == 3


def test_build_task_tree_hide_cancelled():
    """Test build_task_tree hides cancelled tasks by default."""
    now = datetime.now(timezone.utc)
    tasks = [
        Task(
            id=uuid4(),
            title="Task 1",
            status=TaskStatus.TODO,
            created_at=now,
            updated_at=now,
        ),
        Task(
            id=uuid4(),
            title="Task 2",
            status=TaskStatus.CANCELLED,
            created_at=now,
            updated_at=now,
        ),
    ]

    tree = build_task_tree(tasks, show_cancelled=False)
    # Should only show 1 task (the TODO one)
    assert len(tree.children) == 1


def test_build_note_tree_empty():
    """Test build_note_tree with no notes."""
    tree = build_note_tree([])
    assert tree.label == "📝 [bold note]Notes[/bold note]"
    assert len(tree.children) == 1  # "(No notes)" message


def test_build_note_tree_single_note():
    """Test build_note_tree with a single note."""
    now = datetime.now(timezone.utc)
    note = Note(
        id=uuid4(),
        title="Meeting notes",
        content="Discuss project",
        created_at=now,
        updated_at=now,
    )

    tree = build_note_tree([note])
    assert tree.label == "📝 [bold note]Notes[/bold note]"
    assert len(tree.children) == 1


def test_build_note_tree_multiple_notes():
    """Test build_note_tree with multiple notes."""
    now = datetime.now(timezone.utc)
    notes = [
        Note(id=uuid4(), title="Note 1", created_at=now, updated_at=now),
        Note(
            id=uuid4(),
            title="Note 2",
            content="Content",
            created_at=now,
            updated_at=now,
        ),
    ]

    tree = build_note_tree(notes)
    assert tree.label == "📝 [bold note]Notes[/bold note]"
    assert len(tree.children) == 2


def test_build_event_tree_empty():
    """Test build_event_tree with no events."""
    tree = build_event_tree([])
    assert tree.label == "📅 [bold event]Events[/bold event]"
    assert len(tree.children) == 1  # "(No events)" message


def test_build_event_tree_single_event():
    """Test build_event_tree with a single event."""
    now = datetime.now(timezone.utc)
    event = Event(
        id=uuid4(),
        title="Meeting",
        content="This is a very long content that exceeds fifty characters to test truncation",
        occurred_at=now,
        created_at=now,
        updated_at=now,
    )

    tree = build_event_tree([event])
    assert tree.label == "📅 [bold event]Events[/bold event]"
    assert len(tree.children) == 1


def test_build_event_tree_multiple_events():
    """Test build_event_tree with multiple events."""
    now = datetime.now(timezone.utc)
    events = [
        Event(
            id=uuid4(), title="Event 1", occurred_at=now, created_at=now, updated_at=now
        ),
        Event(
            id=uuid4(), title="Event 2", occurred_at=now, created_at=now, updated_at=now
        ),
    ]

    tree = build_event_tree(events)
    assert tree.label == "📅 [bold event]Events[/bold event]"
    assert len(tree.children) == 2


def test_build_log_tree_empty():
    """Test build_log_tree with no entries."""
    date = datetime(2024, 1, 15)
    tree = build_log_tree(date, [], [], [])

    assert "Daily Log: 2024-01-15" in tree.label
    assert len(tree.children) == 1  # "(No entries)" message


def test_build_log_tree_with_tasks():
    """Test build_log_tree with tasks."""
    now = datetime.now(timezone.utc)
    date = datetime(2024, 1, 15)
    tasks = [
        Task(
            id=uuid4(),
            title="Task 1",
            status=TaskStatus.TODO,
            priority=1,
            created_at=now,
            updated_at=now,
        )
    ]

    tree = build_log_tree(date, tasks, [], [])
    assert "Daily Log: 2024-01-15" in tree.label
    assert len(tree.children) == 1  # Tasks section


def test_build_log_tree_with_notes():
    """Test build_log_tree with notes."""
    now = datetime.now(timezone.utc)
    date = datetime(2024, 1, 15)
    notes = [Note(id=uuid4(), title="Note 1", created_at=now, updated_at=now)]

    tree = build_log_tree(date, [], notes, [])
    assert "Daily Log: 2024-01-15" in tree.label
    assert len(tree.children) == 1  # Notes section


def test_build_log_tree_with_events():
    """Test build_log_tree with events."""
    now = datetime.now(timezone.utc)
    date = datetime(2024, 1, 15)
    events = [
        Event(
            id=uuid4(), title="Event 1", occurred_at=now, created_at=now, updated_at=now
        )
    ]

    tree = build_log_tree(date, [], [], events)
    assert "Daily Log: 2024-01-15" in tree.label
    assert len(tree.children) == 1  # Events section


def test_build_log_tree_mixed():
    """Test build_log_tree with tasks, notes, and events."""
    now = datetime.now(timezone.utc)
    date = datetime(2024, 1, 15)
    tasks = [
        Task(
            id=uuid4(),
            title="Task 1",
            status=TaskStatus.TODO,
            priority=2,
            created_at=now,
            updated_at=now,
        )
    ]
    notes = [Note(id=uuid4(), title="Note 1", created_at=now, updated_at=now)]
    events = [
        Event(
            id=uuid4(), title="Event 1", occurred_at=now, created_at=now, updated_at=now
        )
    ]

    tree = build_log_tree(date, tasks, notes, events)
    assert "Daily Log: 2024-01-15" in tree.label
    assert len(tree.children) == 3  # Tasks, Notes, and Events sections


def test_build_task_detail_panel():
    """Test build_task_detail_panel creates a panel with task details."""
    now = datetime.now(timezone.utc)
    task = Task(
        id=uuid4(),
        title="Buy milk",
        description="Get whole milk",
        status=TaskStatus.TODO,
        priority=1,
        created_at=now,
        updated_at=now,
    )

    panel = build_task_detail_panel(task)
    assert panel.title == "📋 Task Details"
    # Panel should contain task information in its renderable content


def test_build_task_detail_panel_without_optional_fields():
    """Test build_task_detail_panel with a task without description and priority."""
    now = datetime.now(timezone.utc)
    task = Task(
        id=uuid4(),
        title="Simple task",
        status=TaskStatus.TODO,
        created_at=now,
        updated_at=now,
    )

    panel = build_task_detail_panel(task)
    assert panel.title == "📋 Task Details"


def test_build_note_detail_panel():
    """Test build_note_detail_panel creates a panel with note details."""
    now = datetime.now(timezone.utc)
    note = Note(
        id=uuid4(),
        title="Meeting notes",
        content="Discuss project timeline",
        created_at=now,
        updated_at=now,
    )

    panel = build_note_detail_panel(note)
    assert panel.title == "📝 Note Details"


def test_build_note_detail_panel_without_content():
    """Test build_note_detail_panel with a note without content."""
    now = datetime.now(timezone.utc)
    note = Note(
        id=uuid4(),
        title="Simple note",
        created_at=now,
        updated_at=now,
    )

    panel = build_note_detail_panel(note)
    assert panel.title == "📝 Note Details"


def test_build_event_detail_panel():
    """Test build_event_detail_panel creates a panel with event details."""
    now = datetime.now(timezone.utc)
    event = Event(
        id=uuid4(),
        title="Team meeting",
        content="Weekly sync",
        occurred_at=now,
        created_at=now,
        updated_at=now,
    )

    panel = build_event_detail_panel(event)
    assert panel.title == "📅 Event Details"


def test_build_event_detail_panel_without_content():
    """Test build_event_detail_panel with an event without content."""
    now = datetime.now(timezone.utc)
    event = Event(
        id=uuid4(),
        title="Simple event",
        occurred_at=now,
        created_at=now,
        updated_at=now,
    )

    panel = build_event_detail_panel(event)
    assert panel.title == "📅 Event Details"
