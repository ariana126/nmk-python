from abc import ABC, abstractmethod


class TokenService(ABC):
    @abstractmethod
    def issue_for_user(self, user_id: str) -> str:
        pass
