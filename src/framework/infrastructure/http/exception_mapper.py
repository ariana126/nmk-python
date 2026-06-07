from abc import ABC, abstractmethod

from framework.infrastructure.http import ProblemDetail


class ExceptionMapper(ABC):
    @staticmethod
    @abstractmethod
    def can_map(exception: Exception) -> bool:
        pass

    @staticmethod
    @abstractmethod
    def to_problem_detail(exception: Exception) -> ProblemDetail:
        pass
