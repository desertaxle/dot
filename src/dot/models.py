"""SQLAlchemy ORM models for the bullet journal application."""

import enum
from datetime import date as DateType
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import (
    Column,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""

    pass


class TaskStatus(str, enum.Enum):
    """Status options for tasks."""

    TODO = "todo"
    DONE = "done"
    CANCELLED = "cancelled"


class ProjectType(str, enum.Enum):
    """Types of projects."""

    PROJECT = "project"
    DAILY_LOG = "daily_log"
    WEEKLY_LOG = "weekly_log"
    MONTHLY_LOG = "monthly_log"


# Association tables for many-to-many relationships
task_tags = Table(
    "task_tags",
    Base.metadata,
    Column(
        "task_id", Integer, ForeignKey("task.id", ondelete="CASCADE"), primary_key=True
    ),
    Column(
        "tag_id", Integer, ForeignKey("tag.id", ondelete="CASCADE"), primary_key=True
    ),
)

note_tags = Table(
    "note_tags",
    Base.metadata,
    Column(
        "note_id", Integer, ForeignKey("note.id", ondelete="CASCADE"), primary_key=True
    ),
    Column(
        "tag_id", Integer, ForeignKey("tag.id", ondelete="CASCADE"), primary_key=True
    ),
)

event_tags = Table(
    "event_tags",
    Base.metadata,
    Column(
        "event_id",
        Integer,
        ForeignKey("event.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "tag_id", Integer, ForeignKey("tag.id", ondelete="CASCADE"), primary_key=True
    ),
)


class Project(Base):
    """A project or log (daily, weekly, monthly)."""

    __tablename__ = "project"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    type: Mapped[ProjectType] = mapped_column(
        Enum(ProjectType), default=ProjectType.PROJECT
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Log-specific fields (nullable for project type discrimination)
    date: Mapped[Optional[DateType]] = mapped_column(
        Date, nullable=True
    )  # For DailyLog
    week_start: Mapped[Optional[DateType]] = mapped_column(
        Date, nullable=True
    )  # For WeeklyLog
    year: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True
    )  # For MonthlyLog
    month: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True
    )  # For MonthlyLog

    # Relationships
    log_entries: Mapped[list["LogEntry"]] = relationship(
        "LogEntry", back_populates="project", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Project(id={self.id}, name='{self.name}', type='{self.type.value}')>"


class Task(Base):
    """A task or todo item."""

    __tablename__ = "task"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[TaskStatus] = mapped_column(
        Enum(TaskStatus), default=TaskStatus.TODO
    )
    priority: Mapped[Optional[int]] = mapped_column(Integer)  # 1=high, 2=medium, 3=low
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    tags: Mapped[list["Tag"]] = relationship(
        secondary=task_tags, back_populates="tasks"
    )
    log_entries: Mapped[list["LogEntry"]] = relationship(
        "LogEntry", back_populates="task", cascade="all, delete-orphan"
    )
    recurrence: Mapped[Optional["TaskRecurrence"]] = relationship(
        "TaskRecurrence",
        back_populates="task",
        uselist=False,
        cascade="all, delete-orphan",
    )
    migrations_from: Mapped[list["Migration"]] = relationship(
        "Migration", foreign_keys="Migration.task_id", back_populates="task"
    )

    def __repr__(self) -> str:
        return (
            f"<Task(id={self.id}, title='{self.title}', status='{self.status.value}')>"
        )


class Note(Base):
    """A note or information entry."""

    __tablename__ = "note"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    tags: Mapped[list["Tag"]] = relationship(
        secondary=note_tags, back_populates="notes"
    )
    log_entries: Mapped[list["LogEntry"]] = relationship(
        "LogEntry", back_populates="note", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Note(id={self.id}, title='{self.title}')>"


class Event(Base):
    """An event that happened."""

    __tablename__ = "event"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[Optional[str]] = mapped_column(Text)
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False
    )  # When the event happened
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    tags: Mapped[list["Tag"]] = relationship(
        secondary=event_tags, back_populates="events"
    )
    log_entries: Mapped[list["LogEntry"]] = relationship(
        "LogEntry", back_populates="event", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Event(id={self.id}, title='{self.title}', occurred_at={self.occurred_at})>"


class Tag(Base):
    """A tag for organizing and filtering entries."""

    __tablename__ = "tag"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    # Relationships
    tasks: Mapped[list[Task]] = relationship(secondary=task_tags, back_populates="tags")
    notes: Mapped[list[Note]] = relationship(secondary=note_tags, back_populates="tags")
    events: Mapped[list[Event]] = relationship(
        secondary=event_tags, back_populates="tags"
    )

    def __repr__(self) -> str:
        return f"<Tag(id={self.id}, name='{self.name}')>"


class LogEntry(Base):
    """An entry in a log (daily, weekly, or monthly) that references a task, note, or event."""

    __tablename__ = "log_entry"

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(
        ForeignKey("project.id", ondelete="CASCADE"), nullable=False
    )
    task_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("task.id", ondelete="CASCADE")
    )
    note_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("note.id", ondelete="CASCADE")
    )
    event_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("event.id", ondelete="CASCADE")
    )
    entry_date: Mapped[datetime] = mapped_column(
        DateTime, nullable=False
    )  # The date this entry appears in the log
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    project: Mapped[Project] = relationship("Project", back_populates="log_entries")
    task: Mapped[Optional[Task]] = relationship("Task", back_populates="log_entries")
    note: Mapped[Optional[Note]] = relationship("Note", back_populates="log_entries")
    event: Mapped[Optional[Event]] = relationship("Event", back_populates="log_entries")
    migrations_to: Mapped[list["Migration"]] = relationship(
        "Migration",
        foreign_keys="Migration.to_log_entry_id",
        back_populates="to_log_entry",
    )
    migrations_from: Mapped[list["Migration"]] = relationship(
        "Migration",
        foreign_keys="Migration.from_log_entry_id",
        back_populates="from_log_entry",
    )

    def __repr__(self) -> str:
        entry_type = "unknown"
        if self.task_id:
            entry_type = "task"
        elif self.note_id:
            entry_type = "note"
        elif self.event_id:
            entry_type = "event"
        return f"<LogEntry(id={self.id}, project_id={self.project_id}, type='{entry_type}', date={self.entry_date.date()})>"


class TaskRecurrence(Base):
    """Recurrence settings for a task using cron expressions."""

    __tablename__ = "task_recurrence"

    id: Mapped[int] = mapped_column(primary_key=True)
    task_id: Mapped[int] = mapped_column(
        ForeignKey("task.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    cron_expression: Mapped[str] = mapped_column(
        String(255), nullable=False
    )  # e.g., "0 9 * * MON" for 9am every Monday
    next_occurrence: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    last_occurrence: Mapped[Optional[datetime]] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    task: Mapped[Task] = relationship("Task", back_populates="recurrence")

    def __repr__(self) -> str:
        return f"<TaskRecurrence(id={self.id}, task_id={self.task_id}, cron='{self.cron_expression}')>"


class Migration(Base):
    """Audit trail for task migrations between log entries."""

    __tablename__ = "migration"

    id: Mapped[int] = mapped_column(primary_key=True)
    task_id: Mapped[int] = mapped_column(
        ForeignKey("task.id", ondelete="CASCADE"), nullable=False
    )
    from_log_entry_id: Mapped[int] = mapped_column(
        ForeignKey("log_entry.id", ondelete="CASCADE"), nullable=False
    )
    to_log_entry_id: Mapped[int] = mapped_column(
        ForeignKey("log_entry.id", ondelete="CASCADE"), nullable=False
    )
    migrated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    # Relationships
    task: Mapped[Task] = relationship("Task", back_populates="migrations_from")
    from_log_entry: Mapped[LogEntry] = relationship(
        "LogEntry", foreign_keys=[from_log_entry_id], back_populates="migrations_to"
    )
    to_log_entry: Mapped[LogEntry] = relationship(
        "LogEntry", foreign_keys=[to_log_entry_id], back_populates="migrations_from"
    )

    def __repr__(self) -> str:
        return f"<Migration(id={self.id}, task_id={self.task_id}, from={self.from_log_entry_id}, to={self.to_log_entry_id})>"
