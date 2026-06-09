from ddd import ValueObject

from framework.domain import DomainException


class InvalidHeartRate(DomainException):
    def __init__(self, message: str, rate: int) -> None:
        super().__init__(message)
        self.rate = rate

    @staticmethod
    def provided(rate: int) -> "InvalidHeartRate":
        return InvalidHeartRate(f"Invalid heart rate provided: {rate}", rate)


class HeartRate(ValueObject):
    def __init__(self, value: int) -> None:
        if 1 > value or 300 < value:
            raise InvalidHeartRate.provided(value)
        self.__value = value

    @staticmethod
    def from_int(value: int) -> "HeartRate":
        return HeartRate(value)

    @property
    def as_int(self) -> int:
        return self.__value

    @property
    def is_out_of_normal_range(self) -> bool:
        return 60 > self.__value or 100 < self.__value
