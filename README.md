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
│   └── infrastructure/         # App bootstrap, Module, DatabaseConnection
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

Domain events are recorded on the aggregate via `_record_that(event)`, then released and published by the repository on save.

---

## Exception Handling

Domain exceptions extend `DomainException` in `framework/domain/exception.py`.

**Adding a new domain exception:**

1. Create an exception class extending `DomainException` in the relevant bounded context.
2. Map it to an HTTP response in the corresponding FastAPI exception handler.

---

## Getting Started

**Prerequisites:** Python 3.10+, PostgreSQL running locally.

```bash
# 1. Install dependencies
make install

# 2. Configure environment
cp .env.example .env
# Fill in DB_HOST, DB_PORT, DB_DATABASE, DB_USERNAME, DB_PASSWORD in .env

# 3. Run database migrations
make migrate

# 4. Start the dev server
make dev
```

---

## Scripts

| Command | Description |
|---|---|
| `make install` | Install dependencies |
| `make dev` | Start with hot reload on :8000 |
| `make start` | Start in production mode on :8000 |
| `make test` | Run unit tests |
| `make bdd` | Run BDD tests |
| `make lint` | Lint with ruff |
| `make lint-fix` | Lint with ruff and auto-fix |
| `make format` | Format with ruff |
| `make migrate` | Apply pending migrations |
| `make migration-create m="..."` | Create a new migration |
| `make migrate-rollback` | Roll back the last migration |
| `make migration-history` | Show migration history |
