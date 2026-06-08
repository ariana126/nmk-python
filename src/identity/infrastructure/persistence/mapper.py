from sqlalchemy import event

from framework.infrastructure.persistence.mapper import mapper_registry
from identity.domain import User
from identity.infrastructure.persistence.tables import users_table

_mappers_configured = False


def start_mappers() -> None:
    global _mappers_configured
    if _mappers_configured:
        return

    mapper_registry.map_imperatively(
        User,
        users_table,
        properties={
            "_id": users_table.c.id,
            "_User__email": users_table.c.email,
            "_User__first_name": users_table.c.first_name,
            "_User__last_name": users_table.c.last_name,
            "_User__password": users_table.c.password,
            "_User__registered_at": users_table.c.registered_at,
        },
    )

    @event.listens_for(User, "load")
    def _on_load(target: User, context) -> None:
        target._AggregateRoot__events = []

    _mappers_configured = True
