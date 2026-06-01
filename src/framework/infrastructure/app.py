from pydm import ServiceContainer, EnvParametersBag
from ddd import Clock
from ddd.infrastructure import SystemClock
from dotenv import load_dotenv

from framework.infrastructure import DatabaseConnection, Module
from identity import IdentityModule


class App:
    __MODULES: tuple[Module] = (IdentityModule,)

    @staticmethod
    def boot() -> None:
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

        for module in App.__MODULES:
            module.boot()