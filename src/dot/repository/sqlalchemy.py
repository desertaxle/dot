"""SQLAlchemy repository implementations for database persistence."""

from datetime import date, datetime, timezone
from typing import List, Optional

import whenever
from sqlalchemy.orm import Session

from dot.domain.log_operations import LogEntry
from dot.domain.models import DailyLog, Event, Note, Project, Task, TaskStatus
from dot.models import Event as OrmEvent
from dot.models import LogEntry as OrmLogEntry
from dot.models import Note as OrmNote
from dot.models import Project as OrmProject
from dot.models import ProjectType as OrmProjectType
from dot.models import Task as OrmTask
from dot.models import TaskStatus as OrmTaskStatus
from dot.repository.abstract import (
    EventRepository,
    LogEntryRepository,
    NoteRepository,
    ProjectRepository,
    TaskRepository,
)


class SQLAlchemyTaskRepository(TaskRepository):
    """SQLAlchemy implementation of TaskRepository."""

    def __init__(self, session: Session):
        """Initialize with a database session."""
        self.session = session

    def _domain_to_orm(self, task: Task) -> OrmTask:
        """Convert domain Task to ORM Task."""
        orm_status = OrmTaskStatus(task.status.value)
        orm_task = OrmTask(
            id=task.id,
            title=task.title,
            description=task.description,
            status=orm_status,
            priority=task.priority,
            created_at=task.created_at,
            updated_at=task.updated_at,
        )
        return orm_task

    def _orm_to_domain(self, orm_task: OrmTask) -> Task:
        """Convert ORM Task to domain Task."""
        domain_status = TaskStatus(orm_task.status.value)
        task = Task(
            id=orm_task.id,
            title=orm_task.title,
            description=orm_task.description,
            status=domain_status,
            priority=orm_task.priority,
            created_at=orm_task.created_at,
            updated_at=orm_task.updated_at,
        )
        return task

    def add(self, task: Task) -> None:
        """Add a task to the database."""
        orm_task = self._domain_to_orm(task)
        self.session.add(orm_task)
        self.session.flush()

    def get(self, task_id: int) -> Optional[Task]:
        """Get a task by ID from the database."""
        orm_task = self.session.query(OrmTask).filter(OrmTask.id == task_id).first()
        if orm_task is None:
            return None
        return self._orm_to_domain(orm_task)

    def list(self) -> List[Task]:
        """List all tasks from the database."""
        orm_tasks = self.session.query(OrmTask).all()
        return [self._orm_to_domain(orm_task) for orm_task in orm_tasks]

    def update(self, task: Task) -> None:
        """Update an existing task in the database."""
        orm_task = self.session.query(OrmTask).filter(OrmTask.id == task.id).first()
        if orm_task is not None:
            orm_task.title = task.title
            orm_task.description = task.description
            orm_task.status = OrmTaskStatus(task.status.value)
            orm_task.priority = task.priority
            orm_task.updated_at = task.updated_at
            self.session.flush()

    def delete(self, task_id: int) -> None:
        """Delete a task from the database."""
        orm_task = self.session.query(OrmTask).filter(OrmTask.id == task_id).first()
        if orm_task is not None:
            self.session.delete(orm_task)
            self.session.flush()


class SQLAlchemyNoteRepository(NoteRepository):
    """SQLAlchemy implementation of NoteRepository."""

    def __init__(self, session: Session):
        """Initialize with a database session."""
        self.session = session

    def _domain_to_orm(self, note: Note) -> OrmNote:
        """Convert domain Note to ORM Note."""
        orm_note = OrmNote(
            id=note.id,
            title=note.title,
            content=note.content,
            created_at=note.created_at,
            updated_at=note.updated_at,
        )
        return orm_note

    def _orm_to_domain(self, orm_note: OrmNote) -> Note:
        """Convert ORM Note to domain Note."""
        note = Note(
            id=orm_note.id,
            title=orm_note.title,
            content=orm_note.content,
            created_at=orm_note.created_at,
            updated_at=orm_note.updated_at,
        )
        return note

    def add(self, note: Note) -> None:
        """Add a note to the database."""
        orm_note = self._domain_to_orm(note)
        self.session.add(orm_note)
        self.session.flush()

    def get(self, note_id: int) -> Optional[Note]:
        """Get a note by ID from the database."""
        orm_note = self.session.query(OrmNote).filter(OrmNote.id == note_id).first()
        if orm_note is None:
            return None
        return self._orm_to_domain(orm_note)

    def list(self) -> List[Note]:
        """List all notes from the database."""
        orm_notes = self.session.query(OrmNote).all()
        return [self._orm_to_domain(orm_note) for orm_note in orm_notes]

    def update(self, note: Note) -> None:
        """Update an existing note in the database."""
        orm_note = self.session.query(OrmNote).filter(OrmNote.id == note.id).first()
        if orm_note is not None:
            orm_note.title = note.title
            orm_note.content = note.content
            orm_note.updated_at = note.updated_at
            self.session.flush()

    def delete(self, note_id: int) -> None:
        """Delete a note from the database."""
        orm_note = self.session.query(OrmNote).filter(OrmNote.id == note_id).first()
        if orm_note is not None:
            self.session.delete(orm_note)
            self.session.flush()


class SQLAlchemyEventRepository(EventRepository):
    """SQLAlchemy implementation of EventRepository."""

    def __init__(self, session: Session):
        """Initialize with a database session."""
        self.session = session

    def _domain_to_orm(self, event: Event) -> OrmEvent:
        """Convert domain Event to ORM Event."""
        orm_event = OrmEvent(
            id=event.id,
            title=event.title,
            content=event.content,
            occurred_at=event.occurred_at,
            created_at=event.created_at,
            updated_at=event.updated_at,
        )
        return orm_event

    def _orm_to_domain(self, orm_event: OrmEvent) -> Event:
        """Convert ORM Event to domain Event."""
        event = Event(
            id=orm_event.id,
            title=orm_event.title,
            content=orm_event.content,
            occurred_at=orm_event.occurred_at,
            created_at=orm_event.created_at,
            updated_at=orm_event.updated_at,
        )
        return event

    def add(self, event: Event) -> None:
        """Add an event to the database."""
        orm_event = self._domain_to_orm(event)
        self.session.add(orm_event)
        self.session.flush()

    def get(self, event_id: int) -> Optional[Event]:
        """Get an event by ID from the database."""
        orm_event = self.session.query(OrmEvent).filter(OrmEvent.id == event_id).first()
        if orm_event is None:
            return None
        return self._orm_to_domain(orm_event)

    def list(self) -> List[Event]:
        """List all events from the database."""
        orm_events = self.session.query(OrmEvent).all()
        return [self._orm_to_domain(orm_event) for orm_event in orm_events]

    def update(self, event: Event) -> None:
        """Update an existing event in the database."""
        orm_event = self.session.query(OrmEvent).filter(OrmEvent.id == event.id).first()
        if orm_event is not None:
            orm_event.title = event.title
            orm_event.content = event.content
            orm_event.occurred_at = event.occurred_at
            orm_event.updated_at = event.updated_at
            self.session.flush()

    def delete(self, event_id: int) -> None:
        """Delete an event from the database."""
        orm_event = self.session.query(OrmEvent).filter(OrmEvent.id == event_id).first()
        if orm_event is not None:
            self.session.delete(orm_event)
            self.session.flush()


class SQLAlchemyProjectRepository(ProjectRepository):
    """SQLAlchemy implementation of ProjectRepository."""

    def __init__(self, session: Session):
        """Initialize with a database session."""
        self.session = session

    def _domain_to_orm(self, project: Project) -> OrmProject:
        """Convert domain Project to ORM Project."""
        # Determine project type and type-specific fields
        project_type = OrmProjectType.PROJECT
        date_field = None
        week_start_field = None
        year_field = None
        month_field = None

        if isinstance(project, DailyLog):
            project_type = OrmProjectType.DAILY_LOG
            # Convert whenever.Date to Python date
            date_field = date(project.date.year, project.date.month, project.date.day)

        orm_project = OrmProject(
            id=project.id,
            name=project.name,
            description=project.description,
            type=project_type,
            date=date_field,
            week_start=week_start_field,
            year=year_field,
            month=month_field,
            created_at=project.created_at,
            updated_at=project.updated_at,
        )
        return orm_project

    def _orm_to_domain(self, orm_project: OrmProject) -> Project:
        """Convert ORM Project to domain Project."""
        # Convert based on project type
        if (
            orm_project.type == OrmProjectType.DAILY_LOG
            and orm_project.date is not None
        ):
            # Convert Python date to whenever.Date
            whenever_date = whenever.Date(
                orm_project.date.year,
                orm_project.date.month,
                orm_project.date.day,
            )
            return DailyLog(
                id=orm_project.id,
                name=orm_project.name,
                description=orm_project.description,
                date=whenever_date,
                created_at=orm_project.created_at,
                updated_at=orm_project.updated_at,
            )
        else:
            # Regular project
            return Project(
                id=orm_project.id,
                name=orm_project.name,
                description=orm_project.description,
                created_at=orm_project.created_at,
                updated_at=orm_project.updated_at,
            )

    def add(self, project: Project) -> None:
        """Add a project to the database."""
        orm_project = self._domain_to_orm(project)
        # If id is 0, don't set it - let database auto-generate
        self.session.add(orm_project)
        self.session.flush()
        # Update domain object with database-assigned ID
        project.id = orm_project.id

    def get(self, project_id: int) -> Optional[Project]:
        """Get a project by ID from the database."""
        orm_project = (
            self.session.query(OrmProject).filter(OrmProject.id == project_id).first()
        )
        if orm_project is None:
            return None
        return self._orm_to_domain(orm_project)

    def list(self) -> List[Project]:
        """List all projects from the database."""
        orm_projects = self.session.query(OrmProject).all()
        return [self._orm_to_domain(orm_project) for orm_project in orm_projects]

    def update(self, project: Project) -> None:
        """Update an existing project in the database."""
        orm_project = (
            self.session.query(OrmProject).filter(OrmProject.id == project.id).first()
        )
        if orm_project is not None:
            orm_project.name = project.name
            orm_project.description = project.description
            orm_project.updated_at = project.updated_at

            self.session.flush()

    def delete(self, project_id: int) -> None:
        """Delete a project from the database."""
        orm_project = (
            self.session.query(OrmProject).filter(OrmProject.id == project_id).first()
        )
        if orm_project is not None:
            self.session.delete(orm_project)
            self.session.flush()

    def get_daily_log(self, log_date: whenever.Date) -> DailyLog:
        """Get or create a daily log for the given date."""
        # Convert whenever.Date to Python date for query
        py_date = date(log_date.year, log_date.month, log_date.day)

        # Search for existing daily log
        orm_project = (
            self.session.query(OrmProject)
            .filter(
                OrmProject.type == OrmProjectType.DAILY_LOG,
                OrmProject.date == py_date,
            )
            .first()
        )

        if orm_project is not None:
            return self._orm_to_domain(orm_project)  # type: ignore

        # Create new daily log
        now = datetime.now(timezone.utc)
        daily_log = DailyLog(
            id=0,  # Will be assigned by database
            name=f"Daily Log {log_date}",
            date=log_date,
            created_at=now,
            updated_at=now,
        )

        # Add to database
        orm_daily_log = self._domain_to_orm(daily_log)
        self.session.add(orm_daily_log)
        self.session.flush()

        # Update domain object with assigned ID
        daily_log.id = orm_daily_log.id
        return daily_log


class SQLAlchemyLogEntryRepository(LogEntryRepository):
    """SQLAlchemy implementation of LogEntryRepository."""

    def __init__(self, session: Session):
        """Initialize with a database session."""
        self.session = session

    def _domain_to_orm(self, log_entry: LogEntry) -> OrmLogEntry:
        """Convert domain LogEntry to ORM LogEntry."""
        # Convert whenever.Date to datetime for entry_date
        entry_datetime = datetime(
            log_entry.entry_date.year,
            log_entry.entry_date.month,
            log_entry.entry_date.day,
            tzinfo=timezone.utc,
        )

        orm_log_entry = OrmLogEntry(
            id=log_entry.id,
            project_id=log_entry.log_id,  # Domain uses log_id, ORM uses project_id
            task_id=log_entry.task_id,
            note_id=log_entry.note_id,
            event_id=log_entry.event_id,
            entry_date=entry_datetime,
        )
        return orm_log_entry

    def _orm_to_domain(self, orm_log_entry: OrmLogEntry) -> LogEntry:
        """Convert ORM LogEntry to domain LogEntry."""
        # Convert datetime to whenever.Date (use date portion only)
        entry_date = whenever.Date(
            orm_log_entry.entry_date.year,
            orm_log_entry.entry_date.month,
            orm_log_entry.entry_date.day,
        )

        log_entry = LogEntry(
            id=orm_log_entry.id,
            log_id=orm_log_entry.project_id,  # ORM uses project_id, domain uses log_id
            task_id=orm_log_entry.task_id,
            note_id=orm_log_entry.note_id,
            event_id=orm_log_entry.event_id,
            entry_date=entry_date,
        )
        return log_entry

    def add(self, log_entry: LogEntry) -> None:
        """Add a log entry to the database."""
        orm_log_entry = self._domain_to_orm(log_entry)
        self.session.add(orm_log_entry)
        self.session.flush()

    def get(self, entry_id: int) -> Optional[LogEntry]:
        """Get a log entry by ID from the database."""
        orm_log_entry = (
            self.session.query(OrmLogEntry).filter(OrmLogEntry.id == entry_id).first()
        )
        if orm_log_entry is None:
            return None
        return self._orm_to_domain(orm_log_entry)

    def list(self) -> List[LogEntry]:
        """List all log entries from the database."""
        orm_log_entries = self.session.query(OrmLogEntry).all()
        return [self._orm_to_domain(orm_log_entry) for orm_log_entry in orm_log_entries]

    def delete(self, entry_id: int) -> None:
        """Delete a log entry from the database."""
        orm_log_entry = (
            self.session.query(OrmLogEntry).filter(OrmLogEntry.id == entry_id).first()
        )
        if orm_log_entry is not None:
            self.session.delete(orm_log_entry)
            self.session.flush()

    def get_by_log_id(self, log_id: int) -> List[LogEntry]:
        """Get all log entries for a specific log."""
        orm_log_entries = (
            self.session.query(OrmLogEntry)
            .filter(OrmLogEntry.project_id == log_id)
            .order_by(OrmLogEntry.entry_date)
            .all()
        )
        return [self._orm_to_domain(orm_log_entry) for orm_log_entry in orm_log_entries]
