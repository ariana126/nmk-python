# Adding a New Bounded Context

Step-by-step checklist for adding a new bounded context (module) to this project. Use `src/identity/` as the reference implementation throughout.

---

## 1. Create the directory skeleton

```
src/<context>/
├── __init__.py
├── domain/
│   ├── __init__.py
│   ├── <aggregate>.py
│   ├── event/
│   │   ├── __init__.py
│   │   └── <event_name>.py
│   └── service/
│       ├── __init__.py
│       ├── <entity>_repository.py
│       └── <domain_service>.py          # only if needed
├── application/
│   ├── __init__.py
│   ├── command/
│   │   ├── __init__.py
│   │   └── <use_case>.py
│   └── query/                           # only if the context has reads
│       ├── __init__.py
│       └── <query_name>.py
└── infrastructure/
    ├── __init__.py
    ├── module.py
    ├── persistence/
    │   ├── __init__.py
    │   ├── tables.py
    │   ├── mapper.py
    │   └── <entity>_repository.py
    ├── service/                         # only if you have domain service interfaces
    │   ├── __init__.py
    │   └── <concrete_service>.py
    └── http/
        ├── __init__.py
        ├── exception_mapper.py
        └── controller/
            ├── __init__.py
            └── <router_group>.py
```

---

## 2. Domain layer

- [ ] **Aggregate** (`domain/<aggregate>.py`) — extend `AggregateRoot` from `ddd`; add a `@staticmethod` or `@classmethod` factory method; call `self._record_that(SomeEvent(...))` for each state change.
- [ ] **Domain events** (`domain/event/<event_name>.py`) — extend `DomainEvent` from `ddd`; one class per event.
- [ ] **Repository interface** (`domain/service/<entity>_repository.py`) — extend `EntityRepository` from `ddd`; declare any query methods beyond `save`/`find` (e.g., `find_by_email`).
- [ ] **Other domain service interfaces** — define as plain ABCs; keep them free of infrastructure imports.
- [ ] **`domain/__init__.py`** — re-export all public domain types (aggregate, events, interfaces) for clean imports.

---

## 3. Application layer

- [ ] **Command + handler** (`application/command/<use_case>.py`):
  - Command: plain dataclass or `@dataclass` with typed fields.
  - Handler: decorated with `@Mediator.handler`; declare dependencies as constructor params (resolved by the DI container).
  - Raise named domain exceptions (e.g., `UserAlreadyExists`) — **not** HTTP exceptions.
- [ ] **Query + handler** (`application/query/<query_name>.py`) — same pattern as commands; return a read model or domain object.
- [ ] **`application/command/__init__.py`** — export command classes and any domain exceptions raised by handlers.

---

## 4. Infrastructure — persistence

- [ ] **`persistence/tables.py`** — define `Table(...)` objects using the shared `mapper_registry` from `framework.infrastructure.persistence.mapper`; add columns, indexes, and constraints.
- [ ] **`persistence/mapper.py`** — implement `start_mappers()`; call `mapper_registry.map_imperatively(DomainClass, table, properties={...})` using mangled private attribute names (e.g., `_User__email`). Guard against double-registration. Add a SQLAlchemy `load` event listener to reset `_AggregateRoot__events = []` after reconstruction.
- [ ] **`persistence/<entity>_repository.py`** — extend `SQLAlchemyBaseRepository`; implement the repository interface from the domain layer.
- [ ] **`persistence/__init__.py`** — export the concrete repository class.

---

## 5. Infrastructure — services

- [ ] For each domain service interface, create a concrete implementation class.
- [ ] Keep infrastructure imports (bcrypt, JWT, external APIs) inside these classes only.

---

## 6. Infrastructure — HTTP

- [ ] **Controller** (`http/controller/<router_group>.py`) — create an `APIRouter`; inject `CommandBus` / `QueryBus` from the container; use Pydantic models for request/response bodies; use `Depends(get_current_user_id)` for authenticated routes.
- [ ] **`http/controller/__init__.py`** — export all routers (e.g., `patients_router`).
- [ ] **Exception mapper** (`http/exception_mapper.py`) — extend `ExceptionMapper`; implement `can_map(exception) -> bool` and `to_problem_detail(exception) -> ProblemDetail`; map each domain exception to an appropriate HTTP status and RFC 7807 body.
- [ ] **`http/__init__.py`** — export the exception mapper class.

---

## 7. Infrastructure — module

- [ ] **`infrastructure/module.py`** — implement the `Module` ABC (from `framework.infrastructure`):
  - `boot()`: call `start_mappers()`, then bind domain interfaces to concrete implementations in `ServiceContainer`.
  - `get_routers()`: return a tuple of all `APIRouter` instances for this context.
- [ ] **`__init__.py`** (context root) — export the `Module` class:
  ```python
  from .infrastructure.module import <Context>Module
  __all__ = ["<Context>Module"]
  ```

---

## 8. Register the module in the app

Two files to edit:

### `src/app.py`

```python
from <context> import <Context>Module

class App:
    __MODULES: tuple[Module] = (IdentityModule, <Context>Module)  # append
```

If the context emits domain events, also register listeners:

```python
@staticmethod
def __register_event_listeners(event_bus: DomainEventBus) -> None:
    event_bus.register(UserRegistered, [DomainEventLogger])
    event_bus.register(<SomeEvent>, [<SomeListener>])  # add
```

### `src/framework/infrastructure/http/exception_handler.py`

```python
from <context>.infrastructure.http import <Context>ExceptionMapper

_EXCEPTION_MAPPERS: tuple[type(ExceptionMapper), ...] = (
    FrameworkExceptionMapper,
    IdentityExceptionMapper,
    <Context>ExceptionMapper,  # append
)
```

---

## 9. Database migration

First, register the new tables in `migrations/env.py` so Alembic can detect them:

```python
import <context>.infrastructure.persistence.tables  # noqa: F401, E402
```

Then generate and apply the migration:

```bash
make migration-create m="create <context> tables"
make migrate
```

Verify the generated file in `migrations/versions/` before running.

---

## 10. BDD tests

- [ ] **Feature spec** — create `features/specs/<context>/<feature>.feature` with Gherkin scenarios covering the happy path and key error cases.
- [ ] **Step definitions** — create `features/step_definitions/<context>/<feature>_test.py`:
  - Call `scenarios("../../specs/<context>/<feature>.feature")` at the top.
  - Implement `@given`, `@when`, `@then` steps; use the `context` fixture (`{}` dict) to pass HTTP response and auth token state between steps.
  - Reuse steps from `features/step_definitions/common/` (e.g., `http_steps.py`, `auth_steps.py`) — they are loaded via `pytest_plugins` in `conftest.py`.
- [ ] If you write new reusable steps, add them to a file in `features/step_definitions/common/` and register that module in `conftest.py`'s `pytest_plugins` list.
- [ ] Run: `make bdd` (requires `make start-dev` to be running).

---

## 11. Final checklist

Easy-to-miss wiring steps — verify these before calling the context done:

- [ ] `migrations/env.py` — `import <context>.infrastructure.persistence.tables` added
- [ ] `Module.get_routers()` — all routers returned
- [ ] `src/app.py` — module appended to `App.__MODULES`
- [ ] `framework/infrastructure/http/exception_handler.py` — `<Context>ExceptionMapper` added to `_EXCEPTION_MAPPERS` (if the context raises domain exceptions)
- [ ] `src/app.py` — event listeners registered in `__register_event_listeners()` (if the context emits domain events)
- [ ] Migration file in `migrations/versions/` reviewed and applied
