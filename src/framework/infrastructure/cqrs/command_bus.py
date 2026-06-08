import logging

from ddd.application import Command
from mediatr import Mediator

from framework.infrastructure.cqrs.di import handler_class_manager

logger = logging.getLogger("CommandBus")


class CommandBus:
    # TODO: Add audit log
    async def execute(self, command: Command):
        logger.info(
            "executing command", extra={"commandClass": command.__class__.__name__}
        )
        return await Mediator(handler_class_manager=handler_class_manager).send(command)
