from abc import ABC, abstractmethod

from ddd import EntityRepository, AggregateRoot, Identity
from ddd.domain.service.repository import AggregateRootType
from framework.infrastructure import DatabaseConnection, DomainEventBus


class SQLAlchemyBaseRepository(EntityRepository, ABC):
    def __init__(self, connection: DatabaseConnection, event_bus: DomainEventBus):
        self.connection = connection
        self.event_bus = event_bus

    def find(self, _id: Identity) -> AggregateRootType | None:
        with self.connection.get_session() as session:
            return session.get(self.entity, _id)

    def save(self, entity: AggregateRoot) -> None:
        with self.connection.get_session() as session:
            session.add(entity)
            session.commit()
        for event in entity.release_events():
            self.event_bus.publish_in_background(event)

    @property
    @abstractmethod
    def entity(self) -> type[AggregateRootType]:
        pass
