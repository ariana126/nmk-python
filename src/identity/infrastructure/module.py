from pydm import ServiceContainer

from framework.infrastructure import Module
from identity.domain import UserRepository
from identity.infrastructure.persistence import SQLAlchemyUserRepository
from identity.infrastructure.persistence.mapper import start_mappers


class IdentityModule(Module):
    def boot(self) -> None:
        start_mappers()
        service_container: ServiceContainer = ServiceContainer.get_instance()

        service_container.bind(UserRepository, SQLAlchemyUserRepository)