from datetime import datetime

from ddd import Entity, Identity

from patients.domain.value import HeartRate, SystolicBloodPressure, Temperature


class Vitals(Entity):
    def __init__(
        self,
        _id: Identity,
        hear_rate: HeartRate,
        systolic_blood_pressure: SystolicBloodPressure,
        temperature: Temperature,
        recorded_at: datetime,
    ):
        super().__init__(_id)
        self.__hear_rate = hear_rate
        self.__systolic_blood_pressure = systolic_blood_pressure
        self.__temperature = temperature
        self.__recorded_at = recorded_at

    @property
    def recorded_at(self) -> datetime:
        return self.__recorded_at

    @property
    def is_out_of_normal_range(self) -> bool:
        return False
