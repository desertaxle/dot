# CLI Command Contracts

**Feature**: 001-bullet-journal-cli
**Date**: 2025-11-17
**Interface**: Command-line (cyclopts-based)

## Command Structure

All commands follow the pattern: `dot <entity> <action> [arguments] [options]`

## Task Commands

### `dot task create`

**Purpose**: Create a new task

**Signature**:
```bash
dot task create <title> [--description DESCRIPTION]
```

**Arguments**:
- `title` (required): Task title (string, max 500 chars)

**Options**:
- `--description`, `-d`: Optional task description (string, max 5000 chars)

**Output** (success):
```
✓ Task created: <title>
  ID: <uuid>
```

**Output** (error - empty title):
```
✗ Error: Task title cannot be empty
```

**Output** (error - title too long):
```
✗ Error: Task title must be 500 characters or less
```

**Exit Codes**:
- 0: Success
- 1: Validation error

---

### `dot task list`

**Purpose**: List all tasks or filter by status

**Signature**:
```bash
dot task list [--status STATUS]
```

**Options**:
- `--status`, `-s`: Filter by status (TODO, DONE, CANCELLED)

**Output** (tasks exist):
```
Tasks
┏━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┓
┃ ID     ┃ Title         ┃ Status   ┃ Created            ┃
┡━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━┩
│ abc... │ Buy groceries │ TODO     │ 2025-11-17 10:30   │
│ def... │ Write report  │ DONE     │ 2025-11-17 09:15   │
└────────┴───────────────┴──────────┴────────────────────┘
```

**Output** (no tasks):
```
No tasks found.
```

**Exit Codes**:
- 0: Success (even if no tasks)

---

### `dot task done`

**Purpose**: Mark a task as done

**Signature**:
```bash
dot task done <task_id>
```

**Arguments**:
- `task_id` (required): UUID or short ID of the task

**Output** (success):
```
✓ Task marked as DONE: <title>
```

**Output** (error - not found):
```
✗ Error: Task not found: <task_id>
```

**Exit Codes**:
- 0: Success
- 1: Task not found

---

### `dot task cancel`

**Purpose**: Mark a task as cancelled

**Signature**:
```bash
dot task cancel <task_id>
```

**Arguments**:
- `task_id` (required): UUID or short ID of the task

**Output** (success):
```
✓ Task marked as CANCELLED: <title>
```

**Output** (error - not found):
```
✗ Error: Task not found: <task_id>
```

**Exit Codes**:
- 0: Success
- 1: Task not found

---

## Event Commands

### `dot event create`

**Purpose**: Create a new event

**Signature**:
```bash
dot event create <title> [--date DATE] [--description DESCRIPTION]
```

**Arguments**:
- `title` (required): Event title (string, max 500 chars)

**Options**:
- `--date`, `-d`: When the event occurred (ISO format, defaults to now)
- `--description`, `-D`: Optional event description (string, max 5000 chars)

**Output** (success):
```
✓ Event created: <title>
  ID: <uuid>
  Date: <occurred_at>
```

**Output** (error - invalid date):
```
✗ Error: Invalid date format. Use ISO format (YYYY-MM-DD or YYYY-MM-DD HH:MM:SS)
```

**Exit Codes**:
- 0: Success
- 1: Validation error

---

### `dot event list`

**Purpose**: List events, optionally filtered by date or range

**Signature**:
```bash
dot event list [--date DATE] [--range START END]
```

**Options**:
- `--date`, `-d`: Show events for specific date
- `--range`, `-r`: Show events in date range (requires START and END)

**Output** (events exist):
```
Events
┏━━━━━━━━┳━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┓
┃ ID     ┃ Title            ┃ Date               ┃
┡━━━━━━━━╇━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━┩
│ abc... │ Team meeting     │ 2025-11-17 14:00   │
│ def... │ Dentist appt     │ 2025-11-18 09:00   │
└────────┴──────────────────┴────────────────────┘
```

**Output** (no events):
```
No events found.
```

**Exit Codes**:
- 0: Success

---

## Note Commands

### `dot note create`

**Purpose**: Create a new note

**Signature**:
```bash
dot note create <title> <content>
```

**Arguments**:
- `title` (required): Note title (string, max 500 chars)
- `content` (required): Note content (string, max 50000 chars)

**Output** (success):
```
✓ Note created: <title>
  ID: <uuid>
```

**Output** (error - empty content):
```
✗ Error: Note content cannot be empty
```

**Exit Codes**:
- 0: Success
- 1: Validation error

---

### `dot note list`

**Purpose**: List all notes

**Signature**:
```bash
dot note list
```

**Output** (notes exist):
```
Notes
┏━━━━━━━━┳━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┓
┃ ID     ┃ Title            ┃ Created            ┃
┡━━━━━━━━╇━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━┩
│ abc... │ Project ideas    │ 2025-11-17 10:30   │
│ def... │ Meeting notes    │ 2025-11-17 14:15   │
└────────┴──────────────────┴────────────────────┘
```

**Output** (no notes):
```
No notes found.
```

**Exit Codes**:
- 0: Success

---

### `dot note show`

**Purpose**: Display full content of a note

**Signature**:
```bash
dot note show <note_id>
```

**Arguments**:
- `note_id` (required): UUID or short ID of the note

**Output** (success):
```
╭─ Project ideas ─────────────────────────────────╮
│ Created: 2025-11-17 10:30                       │
│                                                  │
│ Build a CLI tool for bullet journaling          │
│ - Track tasks with statuses                     │
│ - Record events with dates                      │
│ - Save notes for later reference                │
╰──────────────────────────────────────────────────╯
```

**Output** (error - not found):
```
✗ Error: Note not found: <note_id>
```

**Exit Codes**:
- 0: Success
- 1: Note not found

---

## Log Commands

### `dot log`

**Purpose**: View daily log (all items for a specific date)

**Signature**:
```bash
dot log [DATE]
```

**Arguments**:
- `DATE` (optional): Date to view (ISO format, defaults to today)

**Output** (items exist):
```
Daily Log - 2025-11-17
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Tasks
┏━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━┓
┃ ID     ┃ Title         ┃ Status   ┃
┡━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━┩
│ abc... │ Buy groceries │ TODO     │
└────────┴───────────────┴──────────┘

Events
┏━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┓
┃ ID     ┃ Title        ┃ Time               ┃
┡━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━┩
│ def... │ Team meeting │ 2025-11-17 14:00   │
└────────┴──────────────┴────────────────────┘

Notes
┏━━━━━━━━┳━━━━━━━━━━━━━━━━┓
┃ ID     ┃ Title          ┃
┡━━━━━━━━╇━━━━━━━━━━━━━━━━┩
│ ghi... │ Project ideas  │
└────────┴────────────────┘
```

**Output** (no items):
```
Daily Log - 2025-11-17
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

No entries for this date.
```

**Exit Codes**:
- 0: Success

---

## Global Options

All commands support these global options:

- `--help`, `-h`: Show help message
- `--version`, `-v`: Show version information

## ID Handling

For all commands that accept IDs:
- Full UUID accepted: `550e8400-e29b-41d4-a716-446655440000`
- Short ID accepted: First 8 characters (`550e8400`)
- Case-insensitive

If short ID is ambiguous (multiple matches), error:
```
✗ Error: Ambiguous ID. Multiple items match '550e8400':
  - 550e8400-e29b-41d4-a716-446655440000 (Buy groceries)
  - 550e8400-f39c-52e5-b827-557766551111 (Write report)

  Please use a longer ID prefix.
```

## Color Output

- Success messages: Green ✓
- Error messages: Red ✗
- TODO tasks: White
- DONE tasks: Green (strikethrough if terminal supports)
- CANCELLED tasks: Red (strikethrough if terminal supports)
- Tables: Cyan headers, white content

Use `--no-color` flag to disable colored output for scripting.

## Date Formats

Accepted date input formats:
- ISO date: `2025-11-17`
- ISO datetime: `2025-11-17 14:30:00`
- ISO datetime with timezone: `2025-11-17T14:30:00-06:00`
- Relative: `today`, `yesterday`, `tomorrow`

## Error Messages

All error messages follow the format:
```
✗ Error: <clear description of what went wrong>
  <optional hint on how to fix it>
```

Examples:
- `✗ Error: Task not found: abc123`
- `✗ Error: Invalid date format. Use ISO format (YYYY-MM-DD)`
- `✗ Error: Title cannot be empty`

## Success Feedback

All success messages include:
1. Success indicator (✓)
2. What was done
3. Key details (ID, title, etc.)

This provides immediate confirmation to the user.
