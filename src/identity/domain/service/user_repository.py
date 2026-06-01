from abc import ABC, abstractmethod

from ddd import EntityRepository

from framework.domain import Email
from identity.domain import User


class UserRepository(EntityRepository, ABC):
    @abstractmethod
    def find_by_email(self, email: Email) -> User|None:
        pass