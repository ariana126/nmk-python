import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Type, TypeVar

from ddd import DomainEvent
from pydm import ServiceContainer

logger = logging.getLogger("DomainEventBus")
service_container = ServiceContainer.get_instance()

T = TypeVar("T", bound="DomainEvent")


class DomainEventListener(ABC):
    @abstractmethod
    async def execute(self, event: DomainEvent):
        pass


class DomainEventBus:
    def __init__(self):
        self.__listeners: dict[type, list[Type[DomainEventListener]]] = {}
        self.__background_tasks: set[asyncio.Task] = set()

    def register(
        self, event: Type[T], listeners: list[Type[DomainEventListener]]
    ) -> None:
        if event not in self.__listeners:
            self.__listeners[event] = []
        self.__listeners[event].extend(listeners)

    def publish_in_background(self, event: DomainEvent) -> None:
        task = asyncio.create_task(self.publish(event))
        self.__background_tasks.add(task)
        task.add_done_callback(self.__background_tasks.discard)

    async def publish(self, event: DomainEvent) -> None:
        logger.info(
            "Publishing domain event",
            extra={
                "eventName": event.__class__.__name__,
                "event": event,
            },
        )
        if type(event) not in self.__listeners:
            return
        await asyncio.gather(
            *(
                self.__execute(listener, event)
                for listener in self.__listeners[type(event)]
            )
        )

    async def __execute(
        self, listener_cls: Type[DomainEventListener], event: DomainEvent
    ) -> None:
        try:
            listener = service_container.get_service(listener_cls)
            await listener.execute(event)
            logger.info(
                "Domain event listener executed",
                extra={
                    "eventName": event.__class__.__name__,
                    "listenerName": listener.__class__.__name__,
                    "event": event,
                },
            )
        except Exception:
            logger.exception(
                "An exception occurred in a domain event listener",
                extra={
                    "eventName": event.__class__.__name__,
                    "listenerName": listener_cls,
                    "event": event,
                },
            )
