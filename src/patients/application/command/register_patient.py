from dataclasses import dataclass
from datetime import datetime

from ddd import Identity
from ddd.application import Command, CommandHandler
from mediatr import Mediator

from framework.domain.value.email import Email
from patients.domain import Patient
from patients.domain.service import PatientRepository

class PatientExists(RuntimeError):
    @staticmethod
    def with_email(email: Email) -> 'PatientExists':
        return PatientExists(f'Patient already exists for {email.as_string}')


@dataclass
class RegisterPatientCommand(Command):
    full_name: str
    date_of_birth: datetime
    email: Email


@Mediator.handler
class RegisterPatientCommandHandler(CommandHandler):
    def __init__(self, repository: PatientRepository):
        self.__repository = repository

    async def handle(self, command: RegisterPatientCommand) -> Identity:
        self.__check_email_is_not_used(command.email)
        patient = Patient.register(
            command.full_name, command.date_of_birth, command.email
        )
        self.__repository.save(patient)
        return patient.id

    def __check_email_is_not_used(self, email: Email) -> None:
        if not self.__repository.find_by_email(email) is None:
            raise PatientExists.with_email(email)
