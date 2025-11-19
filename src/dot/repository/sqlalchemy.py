"""SQLAlchemy repository implementations."""

from datetime import date
from uuid import UUID

from sqlalchemy.orm import Session

from dot.domain.models import Event, Task, TaskStatus
from dot.models import EventORM, TaskORM
from dot.repository.abstract import EventRepository, TaskRepository


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


class SQLAlchemyEventRepository(EventRepository):
    """SQLAlchemy implementation of EventRepository."""

    def __init__(self, session: Session) -> None:
        """Initialize the repository with a database session.

        Args:
            session: SQLAlchemy session
        """
        self._session = session

    def add(self, event: Event) -> None:
        """Add a new event."""
        event_orm = self._to_orm(event)
        self._session.add(event_orm)
        self._session.commit()

    def get(self, event_id: UUID) -> Event | None:
        """Get an event by ID."""
        event_orm = (
            self._session.query(EventORM).filter(EventORM.id == event_id).first()
        )
        if event_orm is None:
            return None
        return self._to_domain(event_orm)

    def list(self) -> list[Event]:
        """List all events."""
        event_orms = self._session.query(EventORM).all()
        return [self._to_domain(event_orm) for event_orm in event_orms]

    def list_by_date(self, target_date: date) -> list[Event]:
        """List events that occurred on a specific date."""
        from datetime import datetime, timedelta

        start_of_day = datetime.combine(target_date, datetime.min.time())
        end_of_day = start_of_day + timedelta(days=1)

        event_orms = (
            self._session.query(EventORM)
            .filter(EventORM.occurred_at >= start_of_day)
            .filter(EventORM.occurred_at < end_of_day)
            .all()
        )
        return [self._to_domain(event_orm) for event_orm in event_orms]

    def list_by_range(self, start_date: date, end_date: date) -> list[Event]:
        """List events within a date range (inclusive)."""
        from datetime import datetime, timedelta

        start_of_range = datetime.combine(start_date, datetime.min.time())
        end_of_range = datetime.combine(end_date, datetime.min.time()) + timedelta(
            days=1
        )

        event_orms = (
            self._session.query(EventORM)
            .filter(EventORM.occurred_at >= start_of_range)
            .filter(EventORM.occurred_at < end_of_range)
            .all()
        )
        return [self._to_domain(event_orm) for event_orm in event_orms]

    def delete(self, event_id: UUID) -> None:
        """Delete an event."""
        event_orm = (
            self._session.query(EventORM).filter(EventORM.id == event_id).first()
        )
        if event_orm is not None:
            self._session.delete(event_orm)
            self._session.commit()

    @staticmethod
    def _to_orm(event: Event) -> EventORM:
        """Convert domain Event to ORM EventORM.

        Args:
            event: Domain event

        Returns:
            ORM event
        """
        return EventORM(
            id=event.id,
            title=event.title,
            description=event.description,
            occurred_at=event.occurred_at,
            created_at=event.created_at,
        )

    @staticmethod
    def _to_domain(event_orm: EventORM) -> Event:
        """Convert ORM EventORM to domain Event.

        Args:
            event_orm: ORM event

        Returns:
            Domain event
        """
        return Event(
            id=event_orm.id,
            title=event_orm.title,
            description=event_orm.description,
            occurred_at=event_orm.occurred_at,
            created_at=event_orm.created_at,
        )
