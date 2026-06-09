from ddd.domain.service.repository import AggregateRootType
from sqlalchemy import select

from framework.domain.value.email import Email
from framework.infrastructure import SQLAlchemyBaseRepository
from patients.domain import Patient
from patients.domain.service import PatientRepository
from patients.infrastructure.persistence.tables import patients_table


class SQLAlchemyPatientRepository(PatientRepository, SQLAlchemyBaseRepository):
    @property
    def entity(self) -> type[AggregateRootType]:
        return Patient

    def find_by_email(self, email: Email):
        with self.connection.get_session() as session:
            return session.execute(
                select(Patient).where(patients_table.c.email == email)
            ).scalar_one_or_none()
