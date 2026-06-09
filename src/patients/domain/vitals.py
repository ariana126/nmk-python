from datetime import datetime

from ddd import Entity, Identity

from patients.domain.value import HeartRate, SystolicBloodPressure, Temperature


class Vitals(Entity):
    def __init__(
        self,
        _id: Identity,
        heart_rate: HeartRate,
        systolic_blood_pressure: SystolicBloodPressure,
        temperature: Temperature,
        recorded_at: datetime,
    ):
        super().__init__(_id)
        self.__heart_rate = heart_rate
        self.__systolic_blood_pressure = systolic_blood_pressure
        self.__temperature = temperature
        self.__recorded_at = recorded_at

    @property
    def recorded_at(self) -> datetime:
        return self.__recorded_at

    @property
    def is_out_of_normal_range(self) -> bool:
        return (
            self.__heart_rate.is_out_of_normal_range
            or self.__systolic_blood_pressure.is_out_of_normal_range
            or self.__temperature.is_out_of_normal_range
        )

    @property
    def as_json(self) -> dict:
        return {
            "id": self.id.as_string,
            "heartRatePerMinute": self.__heart_rate.as_int,
            "systolicBp": self.__systolic_blood_pressure.as_int,
            "temperature": self.__temperature.as_float,
            "recordedAt": str(self.__recorded_at),
        }
