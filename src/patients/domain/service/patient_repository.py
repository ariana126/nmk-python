from abc import ABC, abstractmethod

from ddd import EntityRepository

from framework.domain import Email


class PatientRepository(EntityRepository, ABC):
    @abstractmethod
    def find_by_email(self, email: Email):
        pass
