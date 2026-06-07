from abc import ABC, abstractmethod
from fastapi import APIRouter


class Module(ABC):
    @staticmethod
    @abstractmethod
    def boot() -> None:
        pass

    @staticmethod
    @abstractmethod
    def get_routers() -> tuple[APIRouter]:
        pass
