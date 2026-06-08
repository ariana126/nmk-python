import logging

from ddd import DomainEvent

from framework.infrastructure import DomainEventListener

logger = logging.getLogger("DomainEventLogger")


class DomainEventLogger(DomainEventListener):
    async def execute(self, event: DomainEvent):
        logger.debug(
            "Domain Event Captured",
            extra={
                "eventName": event.__class__.__name__,
                "event": event,
            },
        )
