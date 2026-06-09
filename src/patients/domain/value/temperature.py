from ddd import ValueObject

from framework.domain import DomainException


class InvalidTemperature(DomainException):
    def __init__(self, message: str, temperature: float):
        super().__init__(message)
        self.temperature = temperature

    @staticmethod
    def provided(value: float) -> 'InvalidTemperature':
        return InvalidTemperature(f'Invalid temperature provided: {value}', value)


class Temperature(ValueObject):
    def __init__(self, value: float) -> None:
        self.__validate_temperature(value)
        self.__value = value

    @staticmethod
    def from_float(value: float) -> 'Temperature':
        return Temperature(value)

    @property
    def as_float(self) -> float:
        return self.__value

    @staticmethod
    def __validate_temperature(value: float) -> None:
        if 30.0 > value or 45.0 < value:
            raise InvalidTemperature.provided(value)