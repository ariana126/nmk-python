# Movie Nerd

Minimal DDD-style backend with:

- **FastAPI** HTTP server
- **SQLAlchemy** ORM mappings on domain entities
- **Alembic** migrations

## Requirements

- Python **3.10+**
- Postgres

## Setup

Create a virtualenv and install dependencies:

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e ".[dev]"
```

Create a `.env` file (copy from `.env.example`):

```bash
cp .env.example .env
```

Example `.env`:

```bash
DB_HOST=localhost
DB_PORT=5432
DB_DATABASE=mydb
DB_USERNAME=local
DB_PASSWORD=local

# Token signing secret (set this in real deployments)
AUTH_SECRET=change-me
```

## Run the API

```bash
./scripts/run_http_server.sh --reload
```

Defaults:

- `HOST=0.0.0.0`
- `PORT=8000`

Override:

```bash
HOST=127.0.0.1 PORT=8000 ./scripts/run_http_server.sh --reload
```

Health check:

```bash
curl -i "http://localhost:8000/health"
```

## Migrations

Run migrations with Alembic directly:

```bash
alembic upgrade head
```

Or use the helper script:

```bash
./scripts/migration.sh upgrade-latest
./scripts/migration.sh rollback-latest
./scripts/migration.sh create "your message"
```

## Testing

### Unit tests

```bash
pytest -q
```