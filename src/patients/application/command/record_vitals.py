from dataclasses import dataclass

from ddd import Identity, Clock
from ddd.application import Command, CommandHandler
from mediatr import Mediator

from patients.domain import Patient
from patients.domain.service import PatientRepository
from patients.domain.value import HeartRate, SystolicBloodPressure, Temperature


@dataclass
class RecordVitalsCommand(Command):
    patient_id: Identity
    heart_rate: HeartRate
    systolic_blood_pressure: SystolicBloodPressure
    temperature: Temperature


@Mediator.handler
class RecordVitalsCommandHandler(CommandHandler):
    def __init__(self, repository: PatientRepository, clock: Clock):
        self.__repository = repository
        self.__clock = clock

    async def handle(self, command: RecordVitalsCommand) -> None:
        patient: Patient = self.__repository.get(command.patient_id)
        patient.record_vitals(
            command.heart_rate,
            command.systolic_blood_pressure,
            command.temperature,
            self.__clock.now(),
        )
        self.__repository.save(patient)
