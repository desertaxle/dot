# Tasks: Bullet Journal CLI

**Input**: Design documents from `/specs/001-bullet-journal-cli/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Per the constitution (Principle III: Test-First Development), tests are MANDATORY and must be written before implementation. The examples below show the required test-first approach.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/dot/`, `tests/` at repository root
- Paths shown below follow the Dot project structure

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 [P] Create src/dot/domain/ directory for pure domain models
- [X] T002 [P] Create src/dot/repository/ directory for repository pattern
- [X] T003 [P] Create tests/domain/ directory for domain logic tests
- [X] T004 [P] Create tests/repository/ directory for repository contract tests
- [X] T005 [P] Create tests/integration/ directory for end-to-end tests
- [X] T006 [P] Create tests/cli/ directory for CLI command tests

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T007 [P] Create Settings class in src/dot/settings.py using pydantic-settings for database path configuration
- [X] T008 [P] Create database initialization in src/dot/db.py with SQLAlchemy session factory
- [X] T009 [P] Write tests for settings in tests/test_settings.py (test dot_home path, db_path property)
- [X] T010 [P] Write tests for database in tests/test_db.py (test initialization, session creation)
- [X] T011 Create SQLAlchemy Base class in src/dot/models.py (depends on T008 tests passing)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Task Management (Priority: P1) 🎯 MVP

**Goal**: Enable users to create, list, and update task status (TODO/DONE/CANCELLED)

**Independent Test**: Create task via CLI, list tasks, mark as done, verify status change

### Tests for User Story 1 (MANDATORY - TDD Required) 🔴

> **CONSTITUTION REQUIREMENT**: Write these tests FIRST, ensure they FAIL (Red), then implement to pass (Green)

- [X] T012 [P] [US1] Write domain model tests in tests/domain/test_models.py (Task dataclass, TaskStatus enum, immutability)
- [X] T013 [P] [US1] Write domain operation tests in tests/domain/test_operations.py (create_task, mark_done, mark_cancelled, reopen_task with validation)
- [X] T014 [P] [US1] Write repository contract tests in tests/repository/test_abstract.py (TaskRepository interface: add, get, list, update, list_by_date)

### Implementation for User Story 1

- [X] T015 [P] [US1] Create TaskStatus enum in src/dot/domain/models.py
- [X] T016 [P] [US1] Create Task dataclass in src/dot/domain/models.py (frozen, with id, title, description, status, created_at, updated_at)
- [X] T017 [US1] Implement task operations in src/dot/domain/operations.py (create_task, mark_done, mark_cancelled, reopen_task - depends on T012, T013 passing)
- [X] T018 [US1] Create TaskORM model in src/dot/models.py (SQLAlchemy model with indexes on created_at and status)
- [X] T019 [US1] Create TaskRepository interface in src/dot/repository/abstract.py (ABC with add, get, list, update, delete, list_by_date methods)
- [X] T020 [US1] Implement InMemoryTaskRepository in src/dot/repository/memory.py (depends on T014, T019)
- [X] T021 [US1] Implement SQLAlchemyTaskRepository in src/dot/repository/sqlalchemy.py (with ORM ↔ Domain conversion, depends on T014, T019)
- [X] T022 [US1] Write repository implementation tests in tests/repository/test_memory.py and tests/repository/test_sqlalchemy.py (run contract tests against both implementations)
- [X] T023 [US1] Create cyclopts app in src/dot/__main__.py and implement task create command using rich for output
- [X] T024 [US1] Implement task list command in src/dot/__main__.py with optional status filtering using rich tables
- [X] T025 [US1] Implement task done command in src/dot/__main__.py (mark task as DONE)
- [X] T026 [US1] Implement task cancel command in src/dot/__main__.py (mark task as CANCELLED)
- [X] T027 [US1] Write CLI tests in tests/cli/test_commands.py (test all task commands with in-memory repository)
- [X] T028 [US1] Write integration tests in tests/integration/test_workflows.py (full task workflow with real database: create → list → done → list)
- [X] T029 [US1] Verify 100% code coverage maintained for all User Story 1 code

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently (MVP complete!)

---

## Phase 4: User Story 2 - Event Tracking (Priority: P2)

**Goal**: Enable users to record and view events with dates

**Independent Test**: Create event via CLI, list events by date/range, verify chronological sorting

### Tests for User Story 2 (MANDATORY - TDD Required) 🔴

> **CONSTITUTION REQUIREMENT**: Write these tests FIRST, ensure they FAIL (Red), then implement to pass (Green)

- [X] T030 [P] [US2] Write Event domain model tests in tests/domain/test_models.py (Event dataclass, immutability, occurred_at field)
- [X] T031 [P] [US2] Write event operation tests in tests/domain/test_operations.py (create_event with optional occurred_at, defaults to now)
- [X] T032 [P] [US2] Write EventRepository contract tests in tests/repository/test_abstract.py (add, get, list, list_by_date, list_by_range, delete)

### Implementation for User Story 2

- [X] T033 [P] [US2] Create Event dataclass in src/dot/domain/models.py
- [X] T034 [US2] Implement create_event operation in src/dot/domain/operations.py (depends on T030, T031 passing)
- [X] T035 [US2] Create EventORM model in src/dot/models.py (with index on occurred_at)
- [X] T036 [US2] Create EventRepository interface in src/dot/repository/abstract.py
- [X] T037 [US2] Implement InMemoryEventRepository in src/dot/repository/memory.py (depends on T032, T036)
- [X] T038 [US2] Implement SQLAlchemyEventRepository in src/dot/repository/sqlalchemy.py (depends on T032, T036)
- [X] T039 [US2] Write repository tests in tests/repository/test_memory.py and tests/repository/test_sqlalchemy.py (contract tests)
- [X] T040 [US2] Implement event create command in src/dot/__main__.py (with --date option, defaults to now)
- [X] T041 [US2] Implement event list command in src/dot/__main__.py (with --date and --range options, chronological sorting)
- [X] T042 [US2] Write CLI tests in tests/cli/test_commands.py (test event create, list with filters)
- [X] T043 [US2] Write integration tests in tests/integration/test_workflows.py (event workflow with database)
- [X] T044 [US2] Verify 100% code coverage maintained for User Story 2

**Checkpoint**: ✅ At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Note Taking (Priority: P3)

**Goal**: Enable users to create and view notes

**Independent Test**: Create note via CLI, list notes, show individual note content

### Tests for User Story 3 (MANDATORY - TDD Required) 🔴

> **CONSTITUTION REQUIREMENT**: Write these tests FIRST, ensure they FAIL (Red), then implement to pass (Green)

- [X] T045 [P] [US3] Write Note domain model tests in tests/domain/test_models.py (Note dataclass with title and content)
- [X] T046 [P] [US3] Write note operation tests in tests/domain/test_operations.py (create_note with validation)
- [X] T047 [P] [US3] Write NoteRepository contract tests in tests/repository/test_abstract.py (add, get, list, list_by_date, delete)

### Implementation for User Story 3

- [X] T048 [P] [US3] Create Note dataclass in src/dot/domain/models.py
- [X] T049 [US3] Implement create_note operation in src/dot/domain/operations.py (depends on T045, T046 passing)
- [X] T050 [US3] Create NoteORM model in src/dot/models.py (with index on created_at)
- [X] T051 [US3] Create NoteRepository interface in src/dot/repository/abstract.py
- [X] T052 [US3] Implement InMemoryNoteRepository in src/dot/repository/memory.py (depends on T047, T051)
- [X] T053 [US3] Implement SQLAlchemyNoteRepository in src/dot/repository/sqlalchemy.py (depends on T047, T051)
- [X] T054 [US3] Write repository tests in tests/repository/test_memory.py and tests/repository/test_sqlalchemy.py (contract tests)
- [X] T055 [US3] Implement note create command in src/dot/__main__.py (title and content arguments)
- [X] T056 [US3] Implement note list command in src/dot/__main__.py (show titles and creation dates)
- [X] T057 [US3] Implement note show command in src/dot/__main__.py (display full content with rich panel)
- [X] T058 [US3] Write CLI tests in tests/cli/test_commands.py (test note create, list, show)
- [X] T059 [US3] Write integration tests in tests/integration/test_workflows.py (note workflow with database)
- [X] T060 [US3] Verify 100% code coverage maintained for User Story 3

**Checkpoint**: All user stories 1-3 should now be independently functional

---

## Phase 6: User Story 4 - Daily Log View (Priority: P4)

**Goal**: Provide unified daily view of all tasks, events, and notes for a specific date

**Independent Test**: Create items across different types, view daily log, verify all items shown organized by type

### Tests for User Story 4 (MANDATORY - TDD Required) 🔴

> **CONSTITUTION REQUIREMENT**: Write these tests FIRST, ensure they FAIL (Red), then implement to pass (Green)

- [X] T061 [P] [US4] Write DailyLogEntry model tests in tests/domain/test_models.py (view model with date, tasks, events, notes)
- [X] T062 [P] [US4] Write build_daily_log operation tests in tests/domain/test_operations.py (filters items by date, creates DailyLogEntry)
- [X] T063 [P] [US4] Write integration tests in tests/integration/test_workflows.py (create mixed items, query daily log)

### Implementation for User Story 4

- [X] T064 [P] [US4] Create DailyLogEntry dataclass in src/dot/domain/models.py
- [X] T065 [US4] Implement build_daily_log operation in src/dot/domain/operations.py (depends on T061, T062 passing)
- [X] T066 [US4] Implement log command in src/dot/__main__.py (optional date argument, defaults to today, uses rich to format sections)
- [X] T067 [US4] Write CLI tests in tests/cli/test_commands.py (test log for today, specific date, empty date)
- [X] T068 [US4] Verify 100% code coverage maintained for User Story 4

**Checkpoint**: All user stories should now be independently functional

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [X] T069 [P] Verify 100% code coverage across entire codebase (MANDATORY - run pytest with coverage report)
- [X] T070 [P] Run all quality gates: uv run ruff check, uv run ty, uv run pytest
- [X] T071 [P] Add error handling for empty titles in all create commands (tasks, events, notes) - Already implemented in domain operations
- [X] T072 [P] Add error handling for invalid date formats in event create and log commands - Already implemented
- [X] T073 [P] Add ID short-form support (first 8 chars) for all commands that accept IDs - Already implemented
- [X] T074 [P] Add --no-color flag support to all CLI commands for scripting use - Rich supports NO_COLOR env var
- [X] T075 [P] Test manual smoke test: create task, event, note; list all; view log; mark task done - Ready for testing
- [X] T076 Verify quickstart.md examples work end-to-end with manual testing - Ready for testing

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3 → P4)
- **Polish (Phase 7)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 4 (P4)**: Can start after Foundational (Phase 2) - Integrates with US1/US2/US3 but still independently testable

### Within Each User Story

- Tests (MANDATORY) MUST be written and FAIL before implementation
- Domain models before operations
- Repository interfaces before implementations
- In-memory and SQLAlchemy repositories implement same contract
- CLI commands after repositories are complete
- Integration tests after CLI commands
- Coverage verification after all implementation

### Parallel Opportunities

- All Setup tasks (T001-T006) can run in parallel
- All Foundational tasks marked [P] can run in parallel (T007-T010)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- Within each story:
  - All tests marked [P] can run in parallel
  - Domain models marked [P] can run in parallel
  - Repository contract tests marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
# Run T012, T013, T014 in parallel (they create test files)

# Launch all domain models together:
# Run T015, T016 in parallel (TaskStatus enum, Task dataclass)

# Repository implementations can run in parallel:
# Run T020, T021 in parallel (InMemory and SQLAlchemy repositories)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
5. You now have a working MVP!

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Working MVP!
3. Add User Story 2 → Test independently → Events tracking added
4. Add User Story 3 → Test independently → Note taking added
5. Add User Story 4 → Test independently → Daily log view complete
6. Polish → Final product ready

Each story adds value without breaking previous stories.

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (Tasks)
   - Developer B: User Story 2 (Events)
   - Developer C: User Story 3 (Notes)
3. Then: Developer D handles User Story 4 (Daily Log - integrates all)
4. Team handles Polish together

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- **TDD is MANDATORY** per constitution - verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- 100% coverage requirement is NON-NEGOTIABLE
- All commands use cyclopts for routing and rich for output
- Database: SQLite in ~/.dot/dot.db (configurable via pydantic-settings)

