import pytest
from alembic import command
from alembic.config import Config
from starlette.testclient import TestClient
from pydm import ServiceContainer

from app import App
from framework.infrastructure import DatabaseConnection
from framework.infrastructure.persistence.mapper import mapper_registry

pytest_plugins = [
    "features.step_definitions.common.http_steps",
    "features.step_definitions.common.auth_steps",
]


@pytest.fixture(scope="session")
def _app():
    return App.boot()


@pytest.fixture(scope="session", autouse=True)
def run_migrations(_app):
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")


@pytest.fixture(scope="session")
def client(_app, run_migrations):
    with TestClient(_app, raise_server_exceptions=False) as c:
        yield c


@pytest.fixture(autouse=True)
def truncate_tables(client):
    # DELETE (RowExclusiveLock) doesn't conflict with AccessShareLock held by
    # unclosed SQLAlchemy sessions, unlike TRUNCATE (AccessExclusiveLock).
    # sorted_tables gives FK-safe dependency order; reverse it for child-first deletion.
    db: DatabaseConnection = ServiceContainer.get_instance().get_service(
        DatabaseConnection
    )
    with db.engine.connect() as conn:
        for table in reversed(mapper_registry.metadata.sorted_tables):
            conn.execute(table.delete())
        conn.commit()
    yield


@pytest.fixture
def context():
    return {}
