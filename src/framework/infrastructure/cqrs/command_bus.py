from ddd.application import Command
from mediatr import Mediator

from framework.infrastructure.cqrs.di import handler_class_manager


class CommandBus:
    # TODO: Add audit log
    async def execute(self, command: Command):
        return await Mediator(handler_class_manager=handler_class_manager).send(command)
