from fastapi import APIRouter
from pydm import ServiceContainer

from framework.infrastructure import Module
from identity.domain import UserRepository
from identity.infrastructure.http.controller import users_router
from identity.infrastructure.persistence import SQLAlchemyUserRepository
from identity.infrastructure.persistence.mapper import start_mappers


class IdentityModule(Module):
    @staticmethod
    def boot() -> None:
        start_mappers()
        service_container: ServiceContainer = ServiceContainer.get_instance()

        service_container.bind(UserRepository, SQLAlchemyUserRepository)

    @staticmethod
    def get_routers() -> tuple[APIRouter]:
        return (users_router,)