from datetime import datetime

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field, field_validator
from pydantic.alias_generators import to_camel
from pydm import ServiceContainer
from ddd import Identity

from framework.domain.value.email import Email, InvalidEmail
from framework.infrastructure.cqrs import CommandBus, QueryBus
from framework.infrastructure.http import require_authentication
from patients.application.command import RegisterPatientCommand
from patients.application.query import GetPatientByIdQuery
from patients.domain import Patient

patients_router = APIRouter(tags=["Patients"], prefix="/patients")
command_bus = ServiceContainer.get_instance().get_service(CommandBus)
query_bus = ServiceContainer.get_instance().get_service(QueryBus)


class RegisterPatientRequest(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "name": "Alice",
                "dateOfBirth": "2004-01-26",
                "email": "alice@example.com",
            }
        },
    )
    name: str = Field()
    date_of_birth: datetime = Field()
    email: str

    @field_validator("email")
    @classmethod
    def validate_email_format(cls, v: str) -> str:
        try:
            Email.from_string(v)
        except InvalidEmail:
            raise ValueError(f"Invalid email address: '{v}'")
        return v


@patients_router.post(
    "/",
    status_code=200,
    summary="Register a new patient",
    dependencies=[Depends(require_authentication)],
)
async def register_patient(r: RegisterPatientRequest) -> JSONResponse:
    patient_id: Identity = await command_bus.execute(
        RegisterPatientCommand(r.name, r.date_of_birth, Email.from_string(r.email))
    )
    return JSONResponse({"id": patient_id.as_string})


@patients_router.get(
    "/{patient_id}",
    status_code=200,
    summary="Get a patient profile",
    dependencies=[Depends(require_authentication)],
)
async def get_patient_profile(patient_id: str) -> JSONResponse:
    patient: Patient = await query_bus.execute(
        GetPatientByIdQuery(Identity.from_string(patient_id))
    )
    return JSONResponse(
        {
            "id": patient.id.as_string,
            "name": patient.full_name,
            "dateOfBirth": str(patient.date_of_birth.date()),
            "email": patient.email.as_string,
        }
    )
