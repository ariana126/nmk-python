from ddd import ValueObject

from framework.domain import DomainException


class InvalidSystolicBloodPressure(DomainException):
    def __init__(self, message: str, value: int) -> None:
        super().__init__(message)
        self.value = value

    @staticmethod
    def provided(value: int) -> "InvalidSystolicBloodPressure":
        return InvalidSystolicBloodPressure(
            f"Invalid systolic blood pressure: {value}", value
        )


class SystolicBloodPressure(ValueObject):
    def __init__(self, value: int) -> None:
        self.__validate_value(value)
        self.__value = value

    @staticmethod
    def from_int(value: int) -> "SystolicBloodPressure":
        return SystolicBloodPressure(value)

    @property
    def as_int(self) -> int:
        return self.__value

    @staticmethod
    def __validate_value(value: int) -> None:
        if 50 > value > 300:
            raise InvalidSystolicBloodPressure.provided(value)

    @property
    def is_out_of_normal_range(self) -> bool:
        return 140 < self.__value
