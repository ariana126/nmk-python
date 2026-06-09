from dataclasses import dataclass

from ddd import Identity
from mediatr import Mediator

from patients.domain import Patient
from patients.domain.service import PatientRepository


@dataclass(frozen=True)
class GetPatientByIdQuery:
    patient_id: Identity


@Mediator.handler
class GetPatientByIdQueryHandler:
    def __init__(self, repository: PatientRepository):
        self.__repository = repository

    async def handle(self, query: GetPatientByIdQuery) -> Patient:
        return self.__repository.get(query.patient_id)