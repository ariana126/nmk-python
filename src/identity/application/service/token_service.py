from abc import ABC, abstractmethod

from ddd import Identity


class TokenService(ABC):
    @abstractmethod
    def issue_for_user(self, user_id: Identity) -> str:
        pass

    @abstractmethod
    def verify(self, token: str) -> Identity | None:
        pass
