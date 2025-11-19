# Feature Specification: Bullet Journal CLI

**Feature Branch**: `001-bullet-journal-cli`
**Created**: 2025-11-17
**Status**: Draft
**Input**: User description: "Build me a Bullet Journal CLI that helps me track tasks, events, and notes."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Task Management (Priority: P1)

As a user, I want to create and manage tasks so that I can track my to-do items and mark them as complete or cancelled.

**Why this priority**: Task management is the core of a bullet journal. Without it, the system provides no immediate value. This is the minimum viable product.

**Independent Test**: Can be fully tested by creating a task via CLI, viewing the task list, marking a task as done, and verifying the status changes. Delivers immediate productivity value by allowing users to track their to-do items.

**Acceptance Scenarios**:

1. **Given** no existing tasks, **When** user creates a new task with a title, **Then** task is saved and appears in the task list
2. **Given** an existing task, **When** user marks it as done, **Then** task status changes to completed
3. **Given** an existing task, **When** user marks it as cancelled, **Then** task status changes to cancelled
4. **Given** multiple tasks, **When** user views the task list, **Then** all tasks are displayed with their current status
5. **Given** a completed task, **When** user views the task list, **Then** completed tasks are visually distinguished from active tasks

---

### User Story 2 - Event Tracking (Priority: P2)

As a user, I want to record events with dates so that I can log significant occurrences and maintain a timeline of what happened.

**Why this priority**: Events provide context and history. While important for a complete bullet journal, users can get value from task management alone initially.

**Independent Test**: Can be tested independently by creating events via CLI, viewing events for specific dates or date ranges, and verifying events are displayed chronologically.

**Acceptance Scenarios**:

1. **Given** I want to log something that happened, **When** I create an event with a title and date, **Then** the event is saved and associated with that date
2. **Given** I want to log something happening now, **When** I create an event without specifying a date, **Then** the event is saved with the current date and time
3. **Given** multiple events exist, **When** I view events for a specific date, **Then** I see all events for that date in chronological order
4. **Given** events span multiple dates, **When** I view events for a date range, **Then** I see all events within that range sorted by date

---

### User Story 3 - Note Taking (Priority: P3)

As a user, I want to create and store notes so that I can capture ideas, thoughts, and information for later reference.

**Why this priority**: Notes add versatility to the bullet journal but aren't critical for basic productivity tracking. Users can function with tasks and events alone.

**Independent Test**: Can be tested by creating notes with titles and content, viewing the note list, and reading individual notes.

**Acceptance Scenarios**:

1. **Given** I have an idea to capture, **When** I create a note with a title and content, **Then** the note is saved and appears in my note list
2. **Given** multiple notes exist, **When** I view my note list, **Then** all notes are displayed with their titles and creation dates
3. **Given** a specific note I want to read, **When** I view that note, **Then** I see the full title and content

---

### User Story 4 - Daily Log View (Priority: P4)

As a user, I want to view a daily log showing all my tasks, events, and notes for a specific day so that I can see everything relevant to that day in one place.

**Why this priority**: A unified daily view enhances the bullet journal experience but depends on having tasks, events, and notes already implemented.

**Independent Test**: Can be tested by creating tasks, events, and notes for specific dates, then viewing a daily log and verifying all items for that date are displayed together.

**Acceptance Scenarios**:

1. **Given** I have tasks, events, and notes, **When** I view today's daily log, **Then** I see all items created or scheduled for today
2. **Given** I want to review a past day, **When** I view a specific date's log, **Then** I see all items associated with that date
3. **Given** a day with no items, **When** I view that day's log, **Then** I see an appropriate empty state message

---

### Edge Cases

- What happens when a user tries to create a task/event/note with an empty title?
- How does the system handle very long task titles or note content?
- What happens when viewing a date far in the past or future?
- How are tasks/events/notes displayed when there are hundreds of items?
- What happens if a user tries to mark an already-completed task as done again?
- How does the system handle invalid date formats when creating events?

## Requirements *(mandatory)*

### Functional Requirements

**Task Management:**

- **FR-001**: System MUST allow users to create tasks with a title and optional description
- **FR-002**: System MUST support three task statuses: TODO (default), DONE, and CANCELLED
- **FR-003**: Users MUST be able to change a task's status from TODO to DONE or CANCELLED
- **FR-004**: System MUST display all tasks with their current status clearly indicated
- **FR-005**: System MUST persist task data so it survives application restarts

**Event Tracking:**

- **FR-006**: System MUST allow users to create events with a title and optional description
- **FR-007**: System MUST allow users to specify a date and time for events
- **FR-008**: System MUST use the current date and time if no date is specified when creating an event
- **FR-009**: System MUST allow users to view events filtered by specific date or date range
- **FR-010**: System MUST display events in chronological order

**Note Taking:**

- **FR-011**: System MUST allow users to create notes with a title and content
- **FR-012**: System MUST store creation timestamps for all notes
- **FR-013**: System MUST allow users to view a list of all notes
- **FR-014**: System MUST allow users to view the full content of individual notes
- **FR-015**: System MUST persist note data so it survives application restarts

**Daily Log:**

- **FR-016**: System MUST provide a unified view showing tasks, events, and notes for a specific date
- **FR-017**: System MUST display daily log items organized by type (tasks, events, notes)
- **FR-018**: System MUST support viewing daily logs for any date (past, present, or future)

**General:**

- **FR-019**: System MUST be accessible via command-line interface
- **FR-020**: All data MUST persist between application sessions
- **FR-021**: System MUST provide clear feedback for all user actions (success and error states)

### Key Entities

- **Task**: Represents a to-do item with a title, optional description, status (TODO/DONE/CANCELLED), and creation timestamp
- **Event**: Represents something that happened or will happen, with a title, optional description, and date/time
- **Note**: Represents captured information with a title, content, and creation timestamp
- **Daily Log Entry**: A view aggregating tasks, events, and notes associated with a specific date

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can create a task, event, or note in under 10 seconds using straightforward commands
- **SC-002**: Users can view their daily log for any date and see all relevant items within 2 seconds
- **SC-003**: System successfully persists all data with zero loss across application restarts
- **SC-004**: Users can manage at least 1000 combined tasks, events, and notes without performance degradation
- **SC-005**: 95% of users can complete their first task creation without consulting documentation, using intuitive command patterns
- **SC-006**: Task status changes are reflected immediately when viewing task lists
- **SC-007**: Events are consistently sorted chronologically with accurate date/time displays
