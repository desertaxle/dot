"""Contract tests for repository interfaces.

These tests ensure that all repository implementations (in-memory, SQLAlchemy)
behave identically according to the repository contract.
"""

from datetime import date, datetime, timedelta
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
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
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
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    task2 = Task(
        id=uuid4(),
        title="Task 2",
        description=None,
        status=TaskStatus.DONE,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
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
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    done_task = Task(
        id=uuid4(),
        title="DONE Task",
        description=None,
        status=TaskStatus.DONE,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
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
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    task_repository.add(task)

    updated_task = Task(
        id=task.id,
        title="Updated",
        description="New description",
        status=TaskStatus.DONE,
        created_at=task.created_at,
        updated_at=datetime.utcnow(),
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
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    task_repository.add(task)
    assert task_repository.get(task.id) is not None

    task_repository.delete(task.id)

    assert task_repository.get(task.id) is None


def test_task_repository_list_by_date(task_repository: TaskRepository) -> None:
    """Test listing tasks created on a specific date."""
    today = datetime.utcnow()
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
