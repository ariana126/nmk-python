from datetime import datetime

from ddd import AggregateRoot, Identity

from framework.domain import Email
from patients.domain import Vitals
from patients.domain.event import PatientRegistered
from patients.domain.event.vitals_recorded import VitalsRecorded
from patients.domain.value import HeartRate, SystolicBloodPressure, Temperature


class Patient(AggregateRoot):
    def __init__(
        self,
        _id: Identity,
        full_name: str,
        date_of_birth: datetime,
        email: Email,
        vitals: list[Vitals],
    ):
        super().__init__(_id)
        self.__full_name = full_name
        self.__date_of_birth = date_of_birth
        self.__email = email
        self.__vitals = vitals

    @staticmethod
    def register(full_name: str, date_of_birth: datetime, email: Email) -> "Patient":
        patient = Patient(
            Identity.new(),
            full_name,
            date_of_birth,
            email,
            []
        )
        patient._record_that(PatientRegistered(patient.id))
        return patient

    def record_vitals(self, hear_rate: HeartRate, systolic_blood_pressure: SystolicBloodPressure, temperature: Temperature, now_time: datetime) -> None:
        vitals = Vitals(
            Identity.new(),
            hear_rate,
            systolic_blood_pressure,
            temperature,
            now_time
        )
        self.__vitals.append(vitals)
        self._record_that(VitalsRecorded(vitals.id))

    @property
    def vitals(self) -> list[Vitals]:
        return self.__vitals
