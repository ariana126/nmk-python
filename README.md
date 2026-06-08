# Nmk Python

A starter template for building reliable, scalable, and maintainable backend applications fast — by delegating implementation to AI agents while keeping humans in the loop for validation and review.

---

## Philosophy

### 1. AI Implements, Humans Validate

The core workflow: AI agents handle implementation; humans own the validation gate. This separation keeps AI productivity high while ensuring quality through deliberate human review at each checkpoint.

### 2. Software Has Two Values

From *Clean Architecture* by Robert C. Martin:

> Software has two values: **functionality** and **structure**. What makes software *soft* — adaptable and changeable — is its structure, not its functionality.

Hardware is hard because you cannot change it cheaply. Software must remain soft. Both values must be continuously validated.

---

## The Validation Layer

The validation layer is the heart of this project. It ensures AI-generated code meets the bar on both dimensions above.

### Functional Validation — BDD

Behavioral tests treat the application as a **black box**. No implementation details are assumed. Tests interact only through exposed API contracts.

```gherkin
# Good — black box
Given a user signs up via POST /auth/signup
Then they should receive a JWT token

# Bad — white box (avoid)
Given a user record exists in the users table
```

Feature specs live under `features/specs/` and are run with `make bdd`. This approach decouples tests from internals, making them resilient to refactors and safe to run against AI-generated implementations.

### Structural Validation

Beyond working code, structure is checked for long-term maintainability:

| Category | What is validated |
|---|---|
| Architecture | DDD layers, Clean Architecture boundaries |
| Code style | Python conventions, naming, formatting |
| OOP & patterns | SOLID principles, appropriate design patterns |
| Security | OWASP top 10, auth, input validation |
| Performance | Query efficiency, N+1 detection, response times |

---

## Tech Stack

| Layer | Choice |
|---|---|
| Language | Python 3.10+ |
| Framework | FastAPI |
| Database | PostgreSQL |
| ORM | SQLAlchemy |
| Migrations | Alembic |
| Architecture | DDD + CQRS |
| CQRS | mediatr |
| DI Container | pydm |
| Unit testing | pytest |
| AI Agent | Claude Code |

---

## Project Structure

```
src/
├── framework/                  # Shared DDD building blocks
│   ├── domain/                 # DomainException
│   │   └── value/              # Email
│   ├── application/            # TokenService interface
│   └── infrastructure/         # App bootstrap, Module, DatabaseConnection, DomainEventBus
│       ├── cqrs/               # CommandBus, QueryBus
│       └── persistence/        # SQLAlchemyBaseRepository, mapper, types
│
└── identity/                   # User identity bounded context
    ├── domain/                 # User aggregate, UserRepository interface
    │   ├── event/              # UserRegistered
    │   └── service/            # PasswordHasher
    ├── application/
    │   ├── command/            # RegisterUserCommand, LoginCommand + handlers
    │   └── query/              # GetUserByIdQuery + handler
    └── infrastructure/         # IdentityModule
        ├── http/
        │   └── controller/     # auth.py (login), user.py (register, profile)
        └── persistence/        # SQLAlchemyUserRepository, mapper, tables
```

## Request Flow

```
Command: Router → CommandBus → CommandHandler → Aggregate.factory() → Repository.save()
Query:   Router → QueryBus  → QueryHandler   → Repository.find()  → return DTO
```

Domain events are recorded on the aggregate via `_record_that(event)`, released on save, and published in the background through `DomainEventBus` (`framework/infrastructure/event_bus.py`), which dispatches each event to its registered `DomainEventListener`s. Listeners are wired at boot in `App.__register_event_listeners` — e.g. `UserRegistered → DomainEventLogger`.

---

## Exception Handling

HTTP error responses follow [RFC 9457 "Problem Details for HTTP APIs"](https://www.rfc-editor.org/rfc/rfc9457) (the standard that obsoletes RFC 7807), served as `application/problem+json` bodies with `type`, `title`, `status`, and optional `detail`, `instance`, and extension members. `ProblemDetail` (`framework/infrastructure/http/problem_detail.py`) is the value object that builds these bodies; `ProblemDetail.for_unknown_error()` is the 500 fallback for exceptions nothing maps.

**How mapping works:** `ExceptionMapper` (`framework/infrastructure/http/exception_mapper.py`) is a strategy interface — `can_map(exception) -> bool` and `to_problem_detail(exception) -> ProblemDetail`. `register_exception_handlers(app)` (`framework/infrastructure/http/exception_handler.py`) registers FastAPI handlers for `RequestValidationError`, `HTTPException`, and the catch-all `Exception`; each resolves a `ProblemDetail` by walking the ordered `_EXCEPTION_MAPPERS` tuple — the first mapper whose `can_map` returns `True` wins, e.g. `(FrameworkExceptionMapper, IdentityExceptionMapper)`. `FrameworkExceptionMapper` covers shared cases (`EntityNotFound`, `InvalidEmail`, `HTTPException`, `RequestValidationError`); `DomainException` (`framework/domain/exception.py`) is the shared base for domain-level exceptions, though contexts are free to raise plain `Exception` subclasses too, as `IdentityExceptionMapper` does for `UserAlreadyExists`/`InvalidCredentials`.

**Adding a new mapped exception** (following `IdentityExceptionMapper` in `identity/infrastructure/http/exception_mapper.py` as a template):

1. Define the exception in the relevant bounded context (e.g. `UserAlreadyExists` and `InvalidCredentials` live in `identity/application/command/`).
2. List it in that context's `ExceptionMapper.can_map` and return its `ProblemDetail` from `to_problem_detail`:
   ```python
   case UserAlreadyExists():
       return ProblemDetail(
           "user-already-exists", "User Already Exists", 409,
           str(exception), None, {"email": exception.email.as_string},
       )
   ```
3. Register the mapper in the `_EXCEPTION_MAPPERS` tuple in `framework/infrastructure/http/exception_handler.py` — order matters, since the first matching mapper wins.

---

## Getting Started

**Prerequisites:** Docker and Docker Compose. PostgreSQL runs as a containerized `db` service — no local install needed.

```bash
# 1. Configure environment
cp .env.example .env
# Fill in DB_HOST, DB_PORT, DB_DATABASE, DB_USERNAME, DB_PASSWORD, JWT_SECRET in .env

# 2. Build the images
make install

# 3. Start the stack (app + db) with hot reload on :8000
make start-dev

# 4. Run database migrations
make migrate
```

Useful follow-ups: `make logs` tails the app's logs, `make shell` opens a shell in the app container, and `make down` stops the stack.

---

## Scripts

The project runs entirely via Docker Compose. Most commands below execute inside the running `app` container (`docker compose exec app ...`).

| Command | Description |
|---|---|
| `make install` | Build the Docker images |
| `make start-dev` | Start the stack with hot reload on :8000 |
| `make start-prod` | Start the stack in production mode on :8000 |
| `make down` | Stop the stack |
| `make restart` | Restart the stack |
| `make status` | Show container status |
| `make logs` | Tail the app container's logs |
| `make shell` | Open a shell in the app container |
| `make test` | Run unit tests |
| `make bdd` | Run BDD tests |
| `make lint` | Lint with ruff |
| `make lint-fix` | Lint with ruff and auto-fix |
| `make format` | Format with ruff |
| `make migrate` | Apply pending migrations |
| `make migration-create m="..."` | Create a new migration |
| `make migrate-rollback` | Roll back the last migration |
| `make migration-history` | Show migration history |
