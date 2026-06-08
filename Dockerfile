# syntax=docker/dockerfile:1

ARG PYTHON_VERSION=3.12-slim

# ---------------------------------------------------------------------------
# Base: shared OS-level setup for all stages
# ---------------------------------------------------------------------------
FROM python:${PYTHON_VERSION} AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

RUN groupadd --gid 1000 app && \
    useradd --uid 1000 --gid app --shell /bin/bash --create-home app && \
    chown app:app /app

# ---------------------------------------------------------------------------
# Builder: bring in dependency manifests + source needed for `pip install`
# ---------------------------------------------------------------------------
FROM base AS builder

COPY pyproject.toml README.md ./
COPY src ./src

# ---------------------------------------------------------------------------
# Dev target: editable install with dev extras; source is bind-mounted at
# runtime so --reload picks up live changes.
# ---------------------------------------------------------------------------
FROM builder AS dev

RUN pip install --upgrade pip && \
    pip install -e ".[dev]"

COPY alembic.ini Makefile ./
COPY migrations ./migrations
COPY features ./features
COPY docker/entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

USER app

EXPOSE 8000

ENTRYPOINT ["entrypoint.sh"]
CMD ["uvicorn", "src.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]

# ---------------------------------------------------------------------------
# Prod target: regular (non-editable) install, no dev extras, self-contained.
# ---------------------------------------------------------------------------
FROM base AS prod

COPY pyproject.toml README.md ./
COPY src ./src
COPY alembic.ini ./
COPY migrations ./migrations

RUN pip install --upgrade pip && \
    pip install .

COPY docker/entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

USER app

EXPOSE 8000

ENTRYPOINT ["entrypoint.sh"]
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
