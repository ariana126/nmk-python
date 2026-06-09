from fastapi import APIRouter
from pydm import ServiceContainer

from framework.infrastructure import Module
from patients.domain.service import PatientRepository
from patients.infrastructure.http.controller.patient import patients_router
from patients.infrastructure.http.controller.vitals import vitals_router
from patients.infrastructure.persistence import SQLAlchemyPatientRepository
from patients.infrastructure.persistence.mapper import start_mappers


class PatientsModule(Module):
    @staticmethod
    def boot() -> None:
        start_mappers()
        service_container = ServiceContainer.get_instance()

        service_container.bind(PatientRepository, SQLAlchemyPatientRepository)

    @staticmethod
    def get_routers() -> tuple[APIRouter, ...]:
        return (patients_router, vitals_router)
