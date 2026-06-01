from abc import ABC, abstractmethod

from ddd import EntityRepository, AggregateRoot, Identity
from ddd.domain.service.repository import AggregateRootType
from sqlalchemy.orm.session import Session

from framework.infrastructure import DatabaseConnection


class SQLAlchemyBaseRepository(EntityRepository, ABC):
    def __init__(self, connection: DatabaseConnection):
        self.connection = connection

    def find(self, _id: Identity) -> AggregateRootType | None:
        return self.connection.get_session().get(self.entity, _id)

    def save(self, entity: AggregateRoot) -> None:
        session: Session = self.connection.get_session()
        session.add(entity)
        session.commit()
        # TODO: Publish domain events from aggregate root.

    @property
    @abstractmethod
    def entity(self) -> type[AggregateRootType]:
        pass