"""SQLAlchemy repository implementations."""

from datetime import date
from uuid import UUID

from sqlalchemy.orm import Session

from dot.domain.models import Task, TaskStatus
from dot.models import TaskORM
from dot.repository.abstract import TaskRepository


class SQLAlchemyTaskRepository(TaskRepository):
    """SQLAlchemy implementation of TaskRepository."""

    def __init__(self, session: Session) -> None:
        """Initialize the repository with a database session.

        Args:
            session: SQLAlchemy session
        """
        self._session = session

    def add(self, task: Task) -> None:
        """Add a new task."""
        task_orm = self._to_orm(task)
        self._session.add(task_orm)
        self._session.commit()

    def get(self, task_id: UUID) -> Task | None:
        """Get a task by ID."""
        task_orm = self._session.query(TaskORM).filter(TaskORM.id == task_id).first()
        if task_orm is None:
            return None
        return self._to_domain(task_orm)

    def list(self, status: TaskStatus | None = None) -> list[Task]:
        """List tasks, optionally filtered by status."""
        query = self._session.query(TaskORM)
        if status is not None:
            query = query.filter(TaskORM.status == status.value)
        task_orms = query.all()
        return [self._to_domain(task_orm) for task_orm in task_orms]

    def update(self, task: Task) -> None:
        """Update an existing task."""
        task_orm = self._session.query(TaskORM).filter(TaskORM.id == task.id).first()
        if task_orm is not None:
            task_orm.title = task.title
            task_orm.description = task.description
            task_orm.status = task.status.value
            task_orm.updated_at = task.updated_at
            self._session.commit()

    def delete(self, task_id: UUID) -> None:
        """Delete a task."""
        task_orm = self._session.query(TaskORM).filter(TaskORM.id == task_id).first()
        if task_orm is not None:
            self._session.delete(task_orm)
            self._session.commit()

    def list_by_date(self, target_date: date) -> list[Task]:
        """List tasks created on a specific date."""
        from datetime import datetime, timedelta

        start_of_day = datetime.combine(target_date, datetime.min.time())
        end_of_day = start_of_day + timedelta(days=1)

        task_orms = (
            self._session.query(TaskORM)
            .filter(TaskORM.created_at >= start_of_day)
            .filter(TaskORM.created_at < end_of_day)
            .all()
        )
        return [self._to_domain(task_orm) for task_orm in task_orms]

    @staticmethod
    def _to_orm(task: Task) -> TaskORM:
        """Convert domain Task to ORM TaskORM.

        Args:
            task: Domain task

        Returns:
            ORM task
        """
        return TaskORM(
            id=task.id,
            title=task.title,
            description=task.description,
            status=task.status.value,
            created_at=task.created_at,
            updated_at=task.updated_at,
        )

    @staticmethod
    def _to_domain(task_orm: TaskORM) -> Task:
        """Convert ORM TaskORM to domain Task.

        Args:
            task_orm: ORM task

        Returns:
            Domain task
        """
        return Task(
            id=task_orm.id,
            title=task_orm.title,
            description=task_orm.description,
            status=TaskStatus(task_orm.status),
            created_at=task_orm.created_at,
            updated_at=task_orm.updated_at,
        )
