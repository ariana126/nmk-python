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

This approach decouples tests from internals, making them resilient to refactors and safe to run against AI-generated implementations.

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
│   └── infrastructure/         # App bootstrap, Module, DatabaseConnection
│       └── persistence/        # SQLAlchemyBaseRepository, mapper, types
│
└── identity/                   # User registration
    ├── domain/                 # User aggregate, UserRepository interface
    │   ├── event/              # UserRegistered
    │   └── service/            # UserRepository
    ├── application/
    │   └── command/            # RegisterUserCommand + handler
    └── infrastructure/         # IdentityModule
        └── persistence/        # SQLAlchemyUserRepository, mapper, tables
```

---

## Request Flow

```
Router → Mediator → CommandHandler → Aggregate.factory() → Repository.save()
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
pip install -e ".[dev]"

# 2. Configure environment
cp .env.example .env
# Fill in DB_HOST, DB_PORT, DB_DATABASE, DB_USERNAME, DB_PASSWORD in .env

# 3. Run database migrations
alembic upgrade head

# 4. Start the dev server
uvicorn main:app --reload
```

---

## Scripts

| Command | Description |
|---|---|
| `pytest` | Run unit tests |
| `uvicorn main:app --reload` | Start with hot reload |
| `alembic upgrade head` | Apply pending migrations |
| `alembic revision --autogenerate -m "..."` | Create a new migration |
| `alembic current` | Show migration status |
