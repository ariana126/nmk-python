from fastapi import APIRouter
from pydm import ServiceContainer

from framework.infrastructure import Module
from identity.application.service import TokenService
from identity.domain import UserRepository, PasswordHasher
from identity.infrastructure.http.controller import users_router, auth_router
from identity.infrastructure.persistence import SQLAlchemyUserRepository
from identity.infrastructure.persistence.mapper import start_mappers
from identity.infrastructure.service import BcryptPasswordHasher, JwtTokenService


class IdentityModule(Module):
    @staticmethod
    def boot() -> None:
        start_mappers()
        service_container: ServiceContainer = ServiceContainer.get_instance()

        service_container.bind(UserRepository, SQLAlchemyUserRepository)
        service_container.bind(PasswordHasher, BcryptPasswordHasher)
        service_container.bind(TokenService, JwtTokenService)
        service_container.bind_parameters(JwtTokenService, {"secret": "JWT_SECRET"})

    @staticmethod
    def get_routers() -> tuple[APIRouter, ...]:
        return (users_router, auth_router)
