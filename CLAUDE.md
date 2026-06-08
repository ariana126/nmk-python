# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

All commands run inside Docker containers. The stack must be up (`make start-dev`) before running `exec`-based targets.

```bash
make install         # docker compose build
make start-dev       # docker compose up -d  (dev target, hot-reload)
make start-prod      # build + start production stack (no volumes, no dev extras)
make down            # docker compose down
make restart         # docker compose restart
make status          # docker compose ps
make logs            # docker compose logs -f app
make shell           # docker compose exec app bash

make test            # pytest src/ inside container (unit tests)
make bdd             # pytest features/ -v inside container (BDD tests, needs running stack)
make lint            # ruff check . inside container
make lint-fix        # ruff check . --fix inside container
make format          # ruff format . inside container

# Run a single test (open a shell first: make shell)
pytest src/framework/domain/value/email_test.py
pytest -k "test_valid_email_address_is_accepted"

# Database migrations (Alembic)
make migrate                       # alembic upgrade head inside container
make migration-create m="message"  # alembic revision --autogenerate -m "message"
make migrate-rollback              # alembic downgrade -1
make migration-history             # alembic history --verbose
```

Alembic is configured: `alembic.ini` points at `migrations/`, and `migrations/env.py` builds its target metadata from the shared `mapper_registry.metadata` (so new tables added via `start_mappers()` are autodetected) and reads DB connection settings from `.env`. Migration files live in `migrations/versions/` (e.g. `create_app_user_table`, `add_first_name_and_last_name_to_app_user`).

## Environment

Copy `.env.example` to `.env` and fill in the PostgreSQL connection values. The app reads `DB_HOST`, `DB_PORT`, `DB_DATABASE`, `DB_USERNAME`, and `DB_PASSWORD` via `python-dotenv`. Other vars: `LOG_PATH` (rotating JSON log file directory), `DEBUG` (`true`/`false`, controls log level), and `JWT_SECRET` (HS256 signing secret used by `JwtTokenService`).

When running via Docker Compose, `DB_HOST` is set to `db` (the Compose service name) automatically in `docker-compose.yml`; you only need to override credentials in `.env` if the defaults (`local`/`local`/`mydb`) don't suit you.

## Docker

The project is fully containerized. `Dockerfile` uses multi-stage builds:

- **`base`** — Python 3.13-slim, installs the package
- **`dev`** (extends `base`) — installs `.[dev]` extras; used by `docker-compose.yml` with volume mounts for `src/`, `migrations/`, `features/`, and `alembic.ini` to enable hot-reload
- **`prod`** (extends `base`) — installs without dev extras, no volumes; used by `docker-compose.prod.yml`

`docker/entrypoint.sh` runs `alembic upgrade head` then starts uvicorn on every container start, so migrations apply automatically.

`docker-compose.yml` spins up two services: `db` (postgres:16-alpine) with a healthcheck, and `app` (dev target) that waits for the database to be healthy before starting.

## Architecture

This is a Python DDD + CQRS backend. All source lives under `src/` and is installed as an editable package.

### Two top-level packages

- **`framework/`** — shared DDD + HTTP building blocks: domain exceptions, value objects, base repository, database connection, DI `Module` base class, `CommandBus`/`QueryBus`, the `TokenService` interface, the `get_current_user_id` auth dependency, and the RFC 7807 problem-detail/exception-mapping infrastructure (see below).
- **`identity/`** — the Identity bounded context: user registration, login (JWT issuance), and profile retrieval.

Each bounded context follows the same three-layer structure:

```
<context>/
  domain/       # Aggregates, value objects, domain events, repository/service interfaces
  application/
    command/    # Write commands + Mediator handlers (e.g. RegisterUserCommand, LoginCommand)
    query/      # Read queries + Mediator handlers (e.g. GetUserByIdQuery)
  infrastructure/
    http/
      controller/  # FastAPI routers
    persistence/   # SQLAlchemy tables, imperative mappers, concrete repositories
    service/       # Concrete implementations of domain/framework service interfaces
    module.py      # Wires DI bindings and exposes routers for this context
```

### Key libraries

| Import name | PyPI package | Purpose | Skill |
|---|---|---|---|
| `ddd` | `dddx` | DDD primitives: `AggregateRoot`, `Identity`, `ValueObject`, `DomainEvent`, `EntityRepository`, `Clock`, `Command` | `.claude/skills/dddx/SKILL.md` |
| `pydm` | `pydmpro` | DI container: `ServiceContainer` (singleton), `EnvParametersBag` | `.claude/skills/pydm/SKILL.md` |
| `underpy` | `underpyx` | OOP guarantees: `Immutable`, `Encapsulated`, `ServiceClass` (base types used by `ddd`) | `.claude/skills/underpy/SKILL.md` |
| `mediatr` | `mediatr` | Mediator/CQRS: `@Mediator.handler` decorator wires commands to handlers | — |
| `fastapi` | `fastapi` | HTTP framework: `APIRouter`, `FastAPI` app instance, Pydantic request models | — |
| `uvicorn` | `uvicorn` | ASGI server used to run the FastAPI app | — |

Read the relevant skill file before writing code that uses `ddd`, `pydm`, or `underpy` — they document constructor conventions, immutability constraints, and common mistakes that aren't obvious from the library source.

### Dependency injection

`ServiceContainer` is a singleton. `App.boot()` registers global bindings (e.g., `Clock`, `DatabaseConnection`) then calls `module.boot()` for each registered `Module` (`Module` is an ABC requiring both `boot()` and `get_routers()`). Each module registers its own bindings (e.g., `UserRepository → SQLAlchemyUserRepository`, `PasswordHasher → BcryptPasswordHasher`, `TokenService → JwtTokenService`) and returns its HTTP routers via `get_routers()`. `App.boot()` collects all routers and mounts them on the FastAPI instance under the `/api` prefix.

Handler constructors declare dependencies as constructor parameters; the container resolves them automatically.

### CommandBus and QueryBus

`framework/infrastructure/cqrs/command_bus.py` and `query_bus.py` provide `CommandBus` and `QueryBus` — thin wrappers around `Mediator` that resolve handlers from the DI container via the shared `handler_class_manager` (`framework/infrastructure/cqrs/di.py`). Controllers obtain whichever bus they need from the container: writes go through `await command_bus.execute(command)`, reads through `await query_bus.execute(query)`. This keeps FastAPI controllers free of Mediator internals. Handlers are wired with `@Mediator.handler` exactly like commands are.

### Authentication

`framework/application/token_service.py` defines the `TokenService` interface (`issue_for_user(user_id: Identity) -> str`, `verify(token: str) -> Identity | None`). The identity context binds it to `JwtTokenService` (`identity/infrastructure/service/jwt_token_service.py`), which issues HS256 JWTs (24h expiry, signed with `JWT_SECRET`) and verifies/decodes them back to an `Identity`.

`framework/infrastructure/http/current_user.py` exposes `get_current_user_id`, a FastAPI dependency (built on `HTTPBearer`) that resolves `TokenService` from the container, verifies the `Authorization: Bearer <token>` header, and returns the authenticated user's `Identity` — raising `HTTPException(401)` if the token is missing/invalid/expired. Controllers that require auth (e.g. `GET /users/me`) declare it via `Depends(get_current_user_id)`.

### HTTP error handling — RFC 7807 Problem Details

`framework/infrastructure/http/` centralizes exception → HTTP response mapping using RFC 7807 "problem detail" JSON bodies:

- `ProblemDetail` — encodes `type`, `title`, `status`, `detail`, `instance`, plus extension members; `ProblemDetail.for_unknown_error()` is the fallback for unmapped exceptions.
- `ExceptionMapper` — abstract strategy with `can_map(exception) -> bool` and `to_problem_detail(exception) -> ProblemDetail`.
- `FrameworkExceptionMapper` — maps shared/framework exceptions (`EntityNotFound`, `InvalidEmail`, `HTTPException`, `RequestValidationError`).
- `register_exception_handlers(app)` (called from `App.boot()`) registers FastAPI handlers for `RequestValidationError`, `HTTPException`, and the catch-all `Exception`, then runs the exception through an ordered tuple of mappers (`_EXCEPTION_MAPPERS` in `exception_handler.py`) and returns the first match as `application/problem+json`.

Each bounded context can plug in its own mapper: e.g. `identity/infrastructure/http/exception_mapper.py` defines `IdentityExceptionMapper`, mapping `UserAlreadyExists` → 409 and `InvalidCredentials` → 401, and is added to `_EXCEPTION_MAPPERS` alongside `FrameworkExceptionMapper`. To add a new context's mapper, extend `ExceptionMapper` and register it in that tuple.

### SQLAlchemy — imperative (classical) mapping

Domain entities are **not** SQLAlchemy declarative models. Tables are defined with `Table(...)` in `persistence/tables.py`, and `mapper_registry.map_imperatively(DomainClass, table, properties={...})` in `persistence/mapper.py` maps private attributes using their mangled names (e.g., `_User__email`).

A `load` event listener re-initializes `_AggregateRoot__events = []` after SQLAlchemy reconstructs an entity from the database, since `__init__` is bypassed on load.

The shared `mapper_registry` lives in `framework/infrastructure/persistence/mapper.py`. All bounded contexts import and reuse it. Call `start_mappers()` once during `Module.boot()` (it is guarded against double-registration).

### Custom SQLAlchemy column types

`IdentityType` and `EmailType` in `framework/infrastructure/persistence/types.py` are `TypeDecorator` subclasses that convert between `Identity`/`Email` value objects and plain strings at the database boundary.

### Domain Event Bus

`framework/infrastructure/event_bus.py` provides `DomainEventBus` and `DomainEventListener`:

- **`DomainEventListener`** — abstract base with a single `async execute(event: DomainEvent)` method; implement this for each handler.
- **`DomainEventBus`** — holds a listener registry (`event type → [listener classes]`) and a set of tracked `asyncio.Task` objects. Resolved from the DI container as a singleton.

Publishing flow:
1. Aggregate records an event: `self._record_that(SomeEvent(...))`
2. `SQLAlchemyBaseRepository.save()` calls `event_bus.publish_in_background(event)` for each event from `aggregate.release_events()`
3. `publish_in_background()` wraps `publish()` in an `asyncio.create_task()` so the HTTP response is not blocked
4. Listeners are resolved from `ServiceContainer` at execution time (late-binding, supports constructor injection)
5. Listener failures are caught and logged; they never propagate to the caller

Registration happens in `App.__register_event_listeners()` in `src/app.py`:
```python
event_bus.register(UserRegistered, [DomainEventLogger])
```

`DomainEventLogger` (`src/framework/infrastructure/domain_event_logger.py`) is the built-in listener that debug-logs every event. To add a new listener: implement `DomainEventListener`, register a binding in the relevant `Module.boot()`, then call `event_bus.register(EventClass, [ListenerClass])` in `App.__register_event_listeners()`.

### Request flow

```
App.boot() → Module.boot() → ServiceContainer wired, routers registered (under /api)
                                        ↓
HTTP request → FastAPI router → controller validates input / resolves
               current user via Depends(get_current_user_id) if auth required
                                        ↓
await command_bus.execute(cmd)  or  await query_bus.execute(query)
        → CommandBus / QueryBus → Mediator → @Mediator.handler
                                        ↓     (handler resolved from DI container)
Handler → Aggregate.factory_method() / domain service → Repository.save() or .find()
                                        ↓
              SQLAlchemyBaseRepository.save() → event_bus.publish_in_background(events)
                                        ↓
                      asyncio background tasks → DomainEventListener.execute(event)

Exceptions ↦ register_exception_handlers() → ExceptionMapper chain
                                        ↳ RFC 7807 ProblemDetail JSON (application/problem+json)
```

Domain events are recorded on the aggregate via `_record_that(event)` (from `AggregateRoot`) and released via `release_events()`. `SQLAlchemyBaseRepository.save()` publishes them asynchronously in the background via `DomainEventBus`.

### Tests

Test files are co-located with source using the `_test.py` suffix convention (e.g., `email_test.py` next to `email.py`). Tests use `pytest` + `assertpy`. `pytest` is configured via `pyproject.toml` and discovers tests automatically from `src/`.

BDD tests live under `features/`. Run unit tests with `make test` and BDD tests with `make bdd`. See `features/CLAUDE.md` for conventions, fixtures, and how to add new feature specs.

### Adding a new bounded context

1. Create `src/<context>/domain/`, `application/command/` (and `application/query/` if the context has reads), `infrastructure/persistence/`, `infrastructure/http/controller/` packages.
2. Define aggregates extending `AggregateRoot`, repository/service interfaces extending `EntityRepository` (or plain ABCs for domain services).
3. Define tables in `infrastructure/persistence/tables.py` using the shared `mapper_registry`.
4. Implement `start_mappers()` and a concrete repository extending `SQLAlchemyBaseRepository`; put concrete service implementations under `infrastructure/service/`.
5. Create FastAPI `APIRouter` controllers in `infrastructure/http/controller/`. If the context raises domain exceptions that need custom HTTP responses, add an `ExceptionMapper` (see HTTP error handling above).
6. Create a `Module` subclass implementing both `boot()` (calls `start_mappers()`, registers bindings in `ServiceContainer`) and `get_routers()` (returns the context's routers — `Module` is an ABC requiring both).
7. Register the module in `App.__MODULES`, and register any new `ExceptionMapper` in `_EXCEPTION_MAPPERS` (`framework/infrastructure/http/exception_handler.py`).
