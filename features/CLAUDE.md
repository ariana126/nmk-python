# features/ — BDD Test Suite

## Running

```bash
make bdd                          # run all BDD tests
PYTHONPATH=src pytest features/ -v -k "register"  # filter by name
```

BDD tests require a live PostgreSQL database and a running migration baseline. `conftest.py` boots the app, runs `alembic upgrade head`, and tears down table rows between each scenario.

## Layout

```
features/
  specs/<context>/<feature>.feature   # Gherkin feature files
  step_definitions/
    common/                           # shared steps (http_steps.py, etc.)
    <context>/<scenario>_test.py      # context-specific steps
  conftest.py                         # session fixtures: app boot, migrations, HTTP client, table truncation
```

## Conventions

- Step definition files use the `_test.py` suffix (e.g., `register_test.py`).
- Each `_test.py` binds its feature file with `scenarios("../../specs/<context>/<feature>.feature")`.
- Shared steps live in `step_definitions/common/` and are loaded via `pytest_plugins` in `conftest.py`.
- Shared steps are named after their concern (`http_steps.py`), not the context they were first written for.
- The `context` fixture (`{}` dict) is how steps pass state (e.g., HTTP response, auth token) across Given/When/Then within a scenario.

## Fixtures (conftest.py)

| Fixture | Scope | Purpose |
|---|---|---|
| `_app` | session | Boots the FastAPI app via `App.boot()` |
| `run_migrations` | session, autouse | Runs `alembic upgrade head` once per session |
| `client` | session | `starlette.testclient.TestClient` wrapping `_app` |
| `truncate_tables` | function, autouse | DELETEs all rows after each scenario (FK-safe order via `mapper_registry.metadata.sorted_tables`) |
| `context` | function | Blank `{}` dict for sharing state between steps |

Table cleanup uses `DELETE` (not `TRUNCATE`) to avoid lock conflicts with unclosed SQLAlchemy sessions. Table order is derived from `mapper_registry.metadata.sorted_tables` reversed, ensuring child rows are deleted before parents.

## Adding a new feature

1. Write the Gherkin spec in `specs/<context>/<feature>.feature`.
2. Create `step_definitions/<context>/<feature>_test.py`.
3. Call `scenarios("../../specs/<context>/<feature>.feature")` at the top of the step file.
4. Implement `@given`, `@when`, `@then` steps; use the `context` fixture to pass response/token state between them.
5. Put any reusable steps in `step_definitions/common/` and register the module in `conftest.py`'s `pytest_plugins` list.
