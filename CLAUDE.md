# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies (requires Python 3.10+)
pip install -e ".[dev]"

# Run all tests
pytest

# Run a single test file
pytest src/framework/domain/value/email_test.py

# Run a single test by name
pytest -k "test_valid_email_address_is_accepted"
```

There are no lint or format commands configured yet.

Database migrations are managed with Alembic (not yet configured in the repo — migration files are absent).

## Environment

Copy `.env.example` to `.env` and fill in the PostgreSQL connection values. The app reads `DB_HOST`, `DB_PORT`, `DB_DATABASE`, `DB_USERNAME`, and `DB_PASSWORD` via `python-dotenv`.

## Architecture

This is a Python DDD + CQRS backend. All source lives under `src/` and is installed as an editable package.

### Two top-level packages

- **`framework/`** — shared DDD building blocks (domain exceptions, value objects, base repository, database connection, DI module base class).
- **`identity/`** — the Identity bounded context (user registration).

Each bounded context follows the same three-layer structure:

```
<context>/
  domain/       # Aggregates, value objects, domain events, repository interfaces
  application/  # Commands + Mediator handlers
  infrastructure/
    persistence/ # SQLAlchemy tables, imperative mappers, concrete repositories
    module.py    # Wires DI bindings for this context
```

### Key libraries

| Import name | PyPI package | Purpose | Skill |
|---|---|---|---|
| `ddd` | `dddx` | DDD primitives: `AggregateRoot`, `Identity`, `ValueObject`, `DomainEvent`, `EntityRepository`, `Clock` | `.claude/skills/dddx/SKILL.md` |
| `pydm` | `pydmpro` | DI container: `ServiceContainer` (singleton), `EnvParametersBag` | `.claude/skills/pydm/SKILL.md` |
| `underpy` | `underpyx` | OOP guarantees: `Immutable`, `Encapsulated`, `ServiceClass` (base types used by `ddd`) | `.claude/skills/underpy/SKILL.md` |
| `mediatr` | `mediatr` | Mediator/CQRS: `@Mediator.handler` decorator wires commands to handlers | — |

Read the relevant skill file before writing code that uses `ddd`, `pydm`, or `underpy` — they document constructor conventions, immutability constraints, and common mistakes that aren't obvious from the library source.

### Dependency injection

`ServiceContainer` is a singleton. `App.boot()` registers global bindings (e.g., `Clock`, `DatabaseConnection`) then calls `module.boot()` for each registered `Module`. Each module registers its own bindings (e.g., `UserRepository → SQLAlchemyUserRepository`).

Handler constructors declare dependencies as constructor parameters; the container resolves them automatically.

### SQLAlchemy — imperative (classical) mapping

Domain entities are **not** SQLAlchemy declarative models. Tables are defined with `Table(...)` in `persistence/tables.py`, and `mapper_registry.map_imperatively(DomainClass, table, properties={...})` in `persistence/mapper.py` maps private attributes using their mangled names (e.g., `_User__email`).

A `load` event listener re-initializes `_AggregateRoot__events = []` after SQLAlchemy reconstructs an entity from the database, since `__init__` is bypassed on load.

The shared `mapper_registry` lives in `framework/infrastructure/persistence/mapper.py`. All bounded contexts import and reuse it. Call `start_mappers()` once during `Module.boot()` (it is guarded against double-registration).

### Custom SQLAlchemy column types

`IdentityType` and `EmailType` in `framework/infrastructure/persistence/types.py` are `TypeDecorator` subclasses that convert between `Identity`/`Email` value objects and plain strings at the database boundary.

### Request flow

```
App.boot() → Module.boot() → ServiceContainer wired
                                        ↓
Mediator.send(command) → @Mediator.handler resolves handler from container
                                        ↓
Handler → Aggregate.factory_method() → Repository.save()
                                        ↓
                               TODO: publish domain events
```

Domain events are recorded on the aggregate via `_record_that(event)` (from `AggregateRoot`) and available via `release_events()`. Event publishing from `SQLAlchemyBaseRepository.save()` is not yet implemented (marked TODO).

### Tests

Test files are co-located with source using the `_test.py` suffix convention (e.g., `email_test.py` next to `email.py`). Tests use `pytest` + `assertpy`. `pytest` is configured via `pyproject.toml` and discovers tests automatically from `src/`.

### Adding a new bounded context

1. Create `src/<context>/domain/`, `application/`, `infrastructure/` packages.
2. Define aggregates extending `AggregateRoot`, repository interfaces extending `EntityRepository`.
3. Define tables in `infrastructure/persistence/tables.py` using the shared `mapper_registry`.
4. Implement `start_mappers()` and a concrete repository extending `SQLAlchemyBaseRepository`.
5. Create a `Module` subclass that calls `start_mappers()` and registers bindings in `ServiceContainer`.
6. Register the module in `App.__MODULES`.
