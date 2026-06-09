from dataclasses import dataclass

from ddd import Identity
from mediatr import Mediator

from patients.domain import Patient, Vitals
from patients.domain.service import PatientRepository


@dataclass(frozen=True)
class FindAlertedPatientVitalsQuery:
    patient_id: Identity


@Mediator.handler
class FindAlertedPatientVitalsQueryHandler:
    def __init__(self, repository: PatientRepository):
        self.__repository = repository

    async def handle(self, query: FindAlertedPatientVitalsQuery) -> list[Vitals]:
        patient: Patient = self.__repository.get(query.patient_id)
        vitals: list[Vitals] = list(
            filter(lambda v: v.is_out_of_normal_range, patient.vitals)
        )
        vitals.sort(key=lambda v: v.recorded_at)
        return vitals
