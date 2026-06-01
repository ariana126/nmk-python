from pydm import ServiceContainer, EnvParametersBag
from ddd import Clock
from ddd.infrastructure import SystemClock
from dotenv import load_dotenv
from fastapi import FastAPI

from framework.infrastructure import DatabaseConnection, Module
from identity import IdentityModule


class App:
    __MODULES: tuple[Module] = (IdentityModule,)

    @staticmethod
    def boot() -> FastAPI:
        service_container: ServiceContainer = ServiceContainer.get_instance()

        load_dotenv()
        service_container.set_parameters(EnvParametersBag())

        service_container.bind(Clock, SystemClock)

        service_container.bind_parameters(DatabaseConnection, {
            'host': 'DB_HOST',
            'port': 'DB_PORT',
            'database': 'DB_DATABASE',
            'username': 'DB_USERNAME',
            'password': 'DB_PASSWORD',
        })

        App.__boot_modules()

        app = FastAPI()
        App.__configure_routes(app)

        return app

    @staticmethod
    def __boot_modules() -> None:
        for module in App.__MODULES:
            module.boot()

    @staticmethod
    def __configure_routes(app: FastAPI) -> None:
        for module in App.__MODULES:
            for router in module.get_routers():
                app.include_router(router)