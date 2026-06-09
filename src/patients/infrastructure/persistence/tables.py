from sqlalchemy import Table, Column, String, DateTime, ForeignKey

from framework.infrastructure.persistence.mapper import mapper_registry
from framework.infrastructure.persistence.types import IdentityType, EmailType
from patients.infrastructure.persistence.types import (
    HeartRateType,
    SystolicBloodPressureType,
    TemperatureType,
)

patients_table = Table(
    "patients",
    mapper_registry.metadata,
    Column("id", IdentityType, primary_key=True),
    Column("email", EmailType, nullable=False, unique=True),
    Column("full_name", String, nullable=False),
    Column("date_of_birth", DateTime, nullable=False),
)

vitals_table = Table(
    "vitals",
    mapper_registry.metadata,
    Column("id", IdentityType, primary_key=True),
    Column("patient_id", IdentityType, ForeignKey("patients.id"), nullable=False),
    Column("heart_rate", HeartRateType, nullable=False),
    Column("systolic_blood_pressure", SystolicBloodPressureType, nullable=False),
    Column("temperature", TemperatureType, nullable=False),
    Column("recorded_at", DateTime, nullable=False),
)
