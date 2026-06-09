from fastapi import APIRouter, Depends
from fastapi.responses import Response, JSONResponse
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel
from pydm import ServiceContainer
from ddd import Identity

from framework.infrastructure.cqrs import CommandBus, QueryBus
from framework.infrastructure.http import require_authentication
from patients.application.command import RecordVitalsCommand
from patients.application.query import (
    FindPatientVitalsQuery,
    FindAlertedPatientVitalsQuery,
)
from patients.domain import Vitals
from patients.domain.value import HeartRate, SystolicBloodPressure, Temperature

vitals_router = APIRouter(tags=["Vitals"], prefix="/patients/{patient_id}/vitals")
command_bus = ServiceContainer.get_instance().get_service(CommandBus)
query_bus = ServiceContainer.get_instance().get_service(QueryBus)


class RecordVitalsRequest(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "heartRatePerMinute": 90,
                "systolicBp": 100,
                "temperature": 37.6,
            }
        },
    )
    heart_rate_per_minute: int = Field(ge=1, le=300)
    systolic_bp: int = Field(ge=50, le=300)
    temperature: float = Field(ge=30.0, le=45.0)


@vitals_router.post(
    "/",
    status_code=201,
    summary="Record new vitals",
    dependencies=[Depends(require_authentication)],
)
async def record_vitals(patient_id: str, request: RecordVitalsRequest) -> Response:
    await command_bus.execute(
        RecordVitalsCommand(
            Identity.from_string(patient_id),
            HeartRate.from_int(request.heart_rate_per_minute),
            SystolicBloodPressure.from_int(request.systolic_bp),
            Temperature.from_float(request.temperature),
        )
    )
    return Response(status_code=201)


@vitals_router.get(
    "/",
    status_code=200,
    summary="Get patient vitals",
    dependencies=[Depends(require_authentication)],
)
async def get_vitals(patient_id: str) -> JSONResponse:
    vitals: list[Vitals] = await query_bus.execute(
        FindPatientVitalsQuery(Identity.from_string(patient_id))
    )
    return JSONResponse([v.as_json for v in vitals])


@vitals_router.get(
    "/alerting",
    status_code=200,
    summary="Get patient alerted vitals",
    dependencies=[Depends(require_authentication)],
)
async def get_alerted_vitals(patient_id: str) -> JSONResponse:
    vitals: list[Vitals] = await query_bus.execute(
        FindAlertedPatientVitalsQuery(Identity.from_string(patient_id))
    )
    return JSONResponse([v.as_json for v in vitals])
