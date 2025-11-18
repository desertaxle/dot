<!--
SYNC IMPACT REPORT
Version: 0.0.0 → 1.0.0
Rationale: Initial constitution establishing core architectural principles

Modified Principles: N/A (initial creation)

Added Sections:
  - Core Principles (5 principles):
    I. Functional Core / Imperative Shell
    II. Repository Pattern
    III. Test-First Development (NON-NEGOTIABLE)
    IV. 100% Code Coverage (NON-NEGOTIABLE)
    V. Simplicity & YAGNI
  - Quality Standards (Code Quality Gates, Documentation, Error Handling)
  - Development Workflow (Feature Development Process, Testing Strategy, Version Control)
  - Governance (Constitution Authority, Amendment Process, Compliance Review)

Removed Sections: N/A

Templates Status:
  ✅ plan-template.md - Updated:
      - Added concrete Constitution Check section with all 5 principles
      - Updated source structure to match Dot project (src/dot/domain/, repository/, etc.)
  ✅ spec-template.md - Verified (no changes needed):
      - Already emphasizes testability and independent user stories
      - Aligns with Test-First Development principle
  ✅ tasks-template.md - Updated:
      - Changed tests from OPTIONAL to MANDATORY per Principle III
      - Added "CONSTITUTION REQUIREMENT" notes emphasizing TDD
      - Updated task paths to match Dot structure (src/dot/domain/, src/dot/repository/)
      - Added coverage verification tasks to each user story and polish phase
      - Resequenced task IDs to avoid conflicts
  ⚠ No command files found in .specify/templates/commands/ (directory doesn't exist)

Follow-up TODOs: None

Derivation Notes:
  - PROJECT_NAME: "Dot" derived from pyproject.toml (name = "dot") and README.md
  - Principles: Inferred from:
    * CLAUDE.md documentation (commits 532b650-3bae59a) describing functional core/imperative shell
    * pyproject.toml showing 100% coverage enforcement (fail_under = 100)
    * Git history showing consistent TDD practices across all features
    * Repository pattern implementation visible in historical src/dot/repository/ structure
    * YAGNI principle evident in clean, minimal dependency list
  - Ratification date: 2024-11-07 (date of commit a7845fc "Add core data model", project inception)
  - Last amended: 2025-11-17 (today, constitution creation date)
-->

# Dot Constitution

## Core Principles

### I. Functional Core / Imperative Shell

All business logic MUST reside in pure, side-effect-free functions. Domain models in `src/dot/domain/` are pure dataclasses with NO database dependencies. All I/O, persistence, and side effects are confined to the imperative shell (repositories, database layer, CLI).

**Rationale**: This separation enables comprehensive testing without infrastructure, faster development cycles, and clearer reasoning about business logic.

### II. Repository Pattern

Data access MUST use the repository pattern with abstract interfaces. Every domain entity requires an abstract repository interface defining its contract. Implementations (in-memory for testing, SQLAlchemy for production) are provided separately.

**Rationale**: Abstract repositories enable testing with in-memory implementations while production uses database persistence, ensuring tests remain fast and infrastructure-independent.

### III. Test-First Development (NON-NEGOTIABLE)

Tests MUST be written before implementation:
- Write contract tests defining expected behavior
- Verify tests fail (Red)
- Implement minimal code to pass tests (Green)
- Refactor while keeping tests green (Refactor)

No implementation proceeds without failing tests first.

**Rationale**: TDD ensures features are driven by requirements, prevents over-engineering, and guarantees testability from design inception.

### IV. 100% Code Coverage (NON-NEGOTIABLE)

Code coverage MUST be 100% with no exceptions. Coverage is enforced at three levels:
- Local pytest runs (configured in pyproject.toml with `fail_under = 100`)
- Pre-commit hooks via prek
- CI/CD pipeline gates (GitHub Actions)

Any pull request reducing coverage below 100% MUST be rejected.

**Rationale**: Complete coverage ensures all code paths are tested, catches regressions immediately, and maintains quality standards as the project grows.

### V. Simplicity & YAGNI

Start with the simplest solution that could work. Complexity MUST be justified in the implementation plan's Complexity Tracking table before introduction. Prefer:
- Pure functions over classes when possible
- Simple data structures (dataclasses, lists, dicts) over frameworks
- Standard library over third-party dependencies
- Explicit code over clever abstractions

**Rationale**: Simple code is easier to understand, test, maintain, and debug. Premature complexity creates technical debt without delivering value.

## Quality Standards

### Code Quality Gates

All code MUST pass these checks before merge:
- **Linting**: ruff (configured in pyproject.toml)
- **Type Checking**: ty (strict mode)
- **Testing**: pytest with 100% coverage
- **Pre-commit**: All prek checks pass

### Documentation Requirements

- Public functions and classes MUST have docstrings
- Complex algorithms MUST include inline comments explaining the "why"
- Architectural decisions MUST be documented in plan.md for features
- Configuration changes MUST update relevant template files

### Error Handling

- User-facing errors MUST provide actionable messages
- System errors MUST be logged with context
- Database operations MUST use transactions (Unit of Work pattern)
- CLI errors MUST exit with appropriate status codes

## Development Workflow

### Feature Development Process

1. **Specification Phase**: Create spec.md with user scenarios and acceptance criteria
2. **Planning Phase**: Create plan.md with architecture, structure, and constitution compliance check
3. **Implementation Phase**: Follow TDD cycle for each task in tasks.md
4. **Review Phase**: Verify all quality gates pass and coverage remains 100%

### Testing Strategy

- **Unit Tests**: Pure domain logic (fast, no I/O)
- **Contract Tests**: Repository interfaces (verify behavior contracts)
- **Integration Tests**: End-to-end workflows with real database
- **CLI Tests**: Command-line interface behavior

### Version Control

- Commits MUST be atomic and focused
- Commit messages MUST follow conventional commits format
- Feature branches MUST be created from main
- PRs MUST pass all CI/CD checks before merge

## Governance

### Constitution Authority

This constitution supersedes all other development practices and documentation. In case of conflict, constitution principles take precedence.

### Amendment Process

Constitution amendments require:
1. Documented justification for the change
2. Impact analysis on existing templates and code
3. Version bump following semantic versioning:
   - MAJOR: Breaking changes to core principles
   - MINOR: New principles or major clarifications
   - PATCH: Wording improvements, typo fixes
4. Synchronization of all dependent templates (spec, plan, tasks)

### Compliance Review

All implementation plans MUST include a Constitution Check section verifying compliance with all principles. Violations MUST be justified in the Complexity Tracking table with:
- What principle is violated
- Why the violation is necessary
- What simpler alternative was rejected and why

### Runtime Development Guidance

For detailed implementation guidance during active development, refer to historical CLAUDE.md files in git history (commits 532b650 through 3bae59a). These provide agent-specific architectural context.

**Version**: 1.0.0 | **Ratified**: 2024-11-07 | **Last Amended**: 2025-11-17
