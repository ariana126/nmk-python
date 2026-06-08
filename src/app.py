import logging
import os
from logging.handlers import RotatingFileHandler

from pydm import ServiceContainer, EnvParametersBag
from ddd import Clock
from ddd.infrastructure import SystemClock
from dotenv import load_dotenv
from fastapi import FastAPI
from pythonjsonlogger import json

from framework.infrastructure import DatabaseConnection, Module
from identity import IdentityModule
from framework.infrastructure import register_exception_handlers


class App:
    __MODULES: tuple[Module] = (IdentityModule,)

    @staticmethod
    def boot() -> FastAPI:
        service_container: ServiceContainer = ServiceContainer.get_instance()

        load_dotenv()
        parameters = EnvParametersBag()
        service_container.set_parameters(parameters)

        service_container.bind(Clock, SystemClock)

        service_container.bind_parameters(
            DatabaseConnection,
            {
                "host": "DB_HOST",
                "port": "DB_PORT",
                "database": "DB_DATABASE",
                "username": "DB_USERNAME",
                "password": "DB_PASSWORD",
            },
        )

        App.__configure_logger(parameters.get('LOG_PATH'), 'true' == parameters.get('DEBUG'))

        App.__boot_modules()

        app = FastAPI(
            title="NMK API",
            version="1.0.0",
            description="NMK backend — Identity and beyond.",
        )
        App.__configure_routes(app)
        register_exception_handlers(app)

        return app

    @staticmethod
    def __boot_modules() -> None:
        for module in App.__MODULES:
            module.boot()

    @staticmethod
    def __configure_routes(app: FastAPI) -> None:
        for module in App.__MODULES:
            for router in module.get_routers():
                app.include_router(router, prefix="/api")

    @staticmethod
    def __configure_logger(log_path: str, debug: bool) -> None:
        resolved_log_path = os.path.expanduser(os.path.expandvars(log_path))
        os.makedirs(resolved_log_path, exist_ok=True)
        logger = logging.getLogger()

        logger.setLevel(logging.INFO if not debug else logging.DEBUG)
        formatter = json.JsonFormatter(
            "%(asctime)s %(levelname)s %(name)s %(message)s"
        )
        handler = RotatingFileHandler(
            os.path.join(resolved_log_path, 'app.log'),
            maxBytes=5_000_000, # ~5M
            backupCount=10
        )

        handler.setFormatter(formatter)
        logger.addHandler(handler)
