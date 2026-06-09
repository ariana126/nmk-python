from dataclasses import dataclass

from ddd import Identity
from mediatr import Mediator

from patients.domain import Vitals, Patient
from patients.domain.service import PatientRepository


@dataclass(frozen=True)
class FindPatientVitalsQuery:
    patient_id: Identity


@Mediator.handler
class FindPatientVitalsQueryHandler:
    def __init__(self, repository: PatientRepository):
        self.__repository = repository

    async def handle(self, query: FindPatientVitalsQuery) -> list[Vitals]:
        patient: Patient = self.__repository.get(query.patient_id)
        vitals = patient.vitals
        vitals.sort(key=lambda v: v.recorded_at)
        return vitals