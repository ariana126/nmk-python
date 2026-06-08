import logging

from mediatr import Mediator

from framework.infrastructure.cqrs.di import handler_class_manager

logger = logging.getLogger("QueryBus")


class QueryBus:
    async def execute(self, query):
        logger.info("executing query", extra={"commandClass": query.__class__.__name__})
        return await Mediator(handler_class_manager=handler_class_manager).send(query)
