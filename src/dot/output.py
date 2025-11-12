"""Rich console output utilities for the Dot CLI."""

from datetime import datetime

from rich.console import Console
from rich.panel import Panel
from rich.theme import Theme
from rich.tree import Tree

from dot.domain.models import Event, Note, Task, TaskStatus

# Custom minimal/clean theme
custom_theme = Theme(
    {
        "task": "cyan",
        "note": "yellow",
        "event": "magenta",
        "success": "green",
        "error": "red",
        "warning": "yellow",
        "metadata": "dim white",
        "status.done": "green",
        "status.cancelled": "red",
        "status.todo": "cyan",
    }
)

# Create console instances
console = Console(theme=custom_theme)
error_console = Console(theme=custom_theme, stderr=True)


def print_success(message: str) -> None:
    """Print a success message."""
    console.print(f"✓ {message}", style="success")


def print_error(message: str) -> None:
    """Print an error message to stderr."""
    error_console.print(f"✗ {message}", style="error")


def _get_status_style(status: TaskStatus) -> str:
    """Get the style for a task status."""
    if status == TaskStatus.DONE:
        return "status.done"
    elif status == TaskStatus.CANCELLED:
        return "status.cancelled"
    else:
        return "status.todo"


def _get_status_symbol(status: TaskStatus) -> str:
    """Get the symbol for a task status."""
    if status == TaskStatus.DONE:
        return "✓"
    elif status == TaskStatus.CANCELLED:
        return "✗"
    else:
        return "○"


def build_task_tree(tasks: list[Task], show_cancelled: bool = False) -> Tree:
    """Build a Tree structure for displaying tasks."""
    tree = Tree("📋 [bold task]Tasks[/bold task]")

    if not tasks:
        tree.add("[metadata](No tasks)[/metadata]")
        return tree

    for task in tasks:
        if task.status == TaskStatus.CANCELLED and not show_cancelled:
            continue

        status_style = _get_status_style(task.status)
        status_symbol = _get_status_symbol(task.status)

        # Build task label
        label = f"[{status_style}]{status_symbol}[/{status_style}] {task.title}"
        if task.priority:
            label += f" [metadata][P{task.priority}][/metadata]"

        task_node = tree.add(label)

        # Add metadata as sub-nodes
        task_node.add(f"[metadata]ID: {task.id}[/metadata]")
        task_node.add(f"[metadata]Status: {task.status.value}[/metadata]")
        if task.description:
            task_node.add(f"[metadata]Description: {task.description}[/metadata]")

    return tree


def build_note_tree(notes: list[Note]) -> Tree:
    """Build a Tree structure for displaying notes."""
    tree = Tree("📝 [bold note]Notes[/bold note]")

    if not notes:
        tree.add("[metadata](No notes)[/metadata]")
        return tree

    for note in notes:
        label = f"[note]{note.title}[/note]"
        note_node = tree.add(label)

        # Add metadata as sub-nodes
        note_node.add(f"[metadata]ID: {note.id}[/metadata]")
        if note.content:
            # Truncate long content for list view
            content_preview = (
                note.content[:50] + "..." if len(note.content) > 50 else note.content
            )
            note_node.add(f"[metadata]{content_preview}[/metadata]")

    return tree


def build_event_tree(events: list[Event]) -> Tree:
    """Build a Tree structure for displaying events."""
    tree = Tree("📅 [bold event]Events[/bold event]")

    if not events:
        tree.add("[metadata](No events)[/metadata]")
        return tree

    for event in events:
        # Format the occurred_at timestamp
        occurred_str = event.occurred_at.strftime("%Y-%m-%d %H:%M")
        label = f"[event]{event.title}[/event] [metadata]- {occurred_str}[/metadata]"
        event_node = tree.add(label)

        # Add metadata as sub-nodes
        event_node.add(f"[metadata]ID: {event.id}[/metadata]")
        if event.content:
            # Truncate long content for list view
            content_preview = (
                event.content[:50] + "..." if len(event.content) > 50 else event.content
            )
            event_node.add(f"[metadata]{content_preview}[/metadata]")

    return tree


def build_log_tree(
    date: datetime,
    tasks: list[Task],
    notes: list[Note],
    events: list[Event],
) -> Tree:
    """Build a Tree structure for displaying daily log entries."""
    date_str = date.strftime("%Y-%m-%d")
    tree = Tree(f"📖 [bold]Daily Log: {date_str}[/bold]")

    # Check if there are any entries
    has_entries = bool(tasks or notes or events)

    if not has_entries:
        tree.add("[metadata](No entries)[/metadata]")
        return tree

    # Add tasks section
    if tasks:
        tasks_node = tree.add("[bold task]Tasks[/bold task]")
        for task in tasks:
            status_style = _get_status_style(task.status)
            status_symbol = _get_status_symbol(task.status)
            label = f"[{status_style}]{status_symbol}[/{status_style}] {task.title}"
            if task.priority:
                label += f" [metadata][P{task.priority}][/metadata]"
            tasks_node.add(label)

    # Add notes section
    if notes:
        notes_node = tree.add("[bold note]Notes[/bold note]")
        for note in notes:
            notes_node.add(f"[note]{note.title}[/note]")

    # Add events section
    if events:
        events_node = tree.add("[bold event]Events[/bold event]")
        for event in events:
            occurred_str = event.occurred_at.strftime("%H:%M")
            events_node.add(
                f"[event]{event.title}[/event] [metadata]- {occurred_str}[/metadata]"
            )

    return tree


def build_task_detail_panel(task: Task) -> Panel:
    """Build a Panel for displaying task details."""
    content_lines = [
        f"[bold]Task:[/bold] {task.title}",
        f"[metadata]ID:[/metadata] {task.id}",
        f"[metadata]Status:[/metadata] [{_get_status_style(task.status)}]{task.status.value}[/{_get_status_style(task.status)}]",
    ]

    if task.description:
        content_lines.append(f"[metadata]Description:[/metadata] {task.description}")

    if task.priority:
        content_lines.append(f"[metadata]Priority:[/metadata] {task.priority}")

    content_lines.extend(
        [
            f"[metadata]Created:[/metadata] {task.created_at.strftime('%Y-%m-%d %H:%M:%S')}",
            f"[metadata]Updated:[/metadata] {task.updated_at.strftime('%Y-%m-%d %H:%M:%S')}",
        ]
    )

    content = "\n".join(content_lines)
    return Panel(content, border_style="task", title="📋 Task Details")


def build_note_detail_panel(note: Note) -> Panel:
    """Build a Panel for displaying note details."""
    content_lines = [
        f"[bold]Note:[/bold] {note.title}",
        f"[metadata]ID:[/metadata] {note.id}",
    ]

    if note.content:
        content_lines.append(f"[metadata]Content:[/metadata]\n{note.content}")

    content_lines.extend(
        [
            f"[metadata]Created:[/metadata] {note.created_at.strftime('%Y-%m-%d %H:%M:%S')}",
            f"[metadata]Updated:[/metadata] {note.updated_at.strftime('%Y-%m-%d %H:%M:%S')}",
        ]
    )

    content = "\n".join(content_lines)
    return Panel(content, border_style="note", title="📝 Note Details")


def build_event_detail_panel(event: Event) -> Panel:
    """Build a Panel for displaying event details."""
    content_lines = [
        f"[bold]Event:[/bold] {event.title}",
        f"[metadata]ID:[/metadata] {event.id}",
        f"[metadata]Occurred:[/metadata] {event.occurred_at.strftime('%Y-%m-%d %H:%M:%S')}",
    ]

    if event.content:
        content_lines.append(f"[metadata]Content:[/metadata]\n{event.content}")

    content_lines.extend(
        [
            f"[metadata]Created:[/metadata] {event.created_at.strftime('%Y-%m-%d %H:%M:%S')}",
            f"[metadata]Updated:[/metadata] {event.updated_at.strftime('%Y-%m-%d %H:%M:%S')}",
        ]
    )

    content = "\n".join(content_lines)
    return Panel(content, border_style="event", title="📅 Event Details")
