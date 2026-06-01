from abc import ABC, abstractmethod


class Module(ABC):
    @abstractmethod
    def boot(self) -> None:
        pass