from sqlalchemy import event
from sqlalchemy.orm import relationship

from framework.infrastructure.persistence.mapper import mapper_registry
from patients.domain import Patient, Vitals
from patients.infrastructure.persistence.tables import patients_table, vitals_table

_mappers_configured = False


def start_mappers() -> None:
    global _mappers_configured
    if _mappers_configured:
        return

    mapper_registry.map_imperatively(
        Vitals,
        vitals_table,
        properties={
            "_id": vitals_table.c.id,
            "_Vitals__heart_rate": vitals_table.c.heart_rate,
            "_Vitals__systolic_blood_pressure": vitals_table.c.systolic_blood_pressure,
            "_Vitals__temperature": vitals_table.c.temperature,
            "_Vitals__recorded_at": vitals_table.c.recorded_at,
        },
    )

    mapper_registry.map_imperatively(
        Patient,
        patients_table,
        properties={
            "_id": patients_table.c.id,
            "_Patient__email": patients_table.c.email,
            "_Patient__full_name": patients_table.c.full_name,
            "_Patient__date_of_birth": patients_table.c.date_of_birth,
            "_Patient__vitals": relationship(
                Vitals,
                cascade="all, delete-orphan",
                lazy="selectin",
            ),
        },
    )

    @event.listens_for(Patient, "load")
    def _on_load(target: Patient, context) -> None:
        target._AggregateRoot__events = []

    _mappers_configured = True
