from sqlalchemy import Integer, Float
from sqlalchemy.types import TypeDecorator

from patients.domain.value import HeartRate, SystolicBloodPressure, Temperature


class HeartRateType(TypeDecorator):
    impl = Integer
    cache_ok = True

    def process_bind_param(self, value, dialect):
        return value.as_int if value is not None else None

    def process_result_value(self, value, dialect):
        return HeartRate.from_int(value) if value is not None else None


class SystolicBloodPressureType(TypeDecorator):
    impl = Integer
    cache_ok = True

    def process_bind_param(self, value, dialect):
        return value.as_int if value is not None else None

    def process_result_value(self, value, dialect):
        return SystolicBloodPressure.from_int(value) if value is not None else None


class TemperatureType(TypeDecorator):
    impl = Float
    cache_ok = True

    def process_bind_param(self, value, dialect):
        return value.as_float if value is not None else None

    def process_result_value(self, value, dialect):
        return Temperature.from_float(value) if value is not None else None
