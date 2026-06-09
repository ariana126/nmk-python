# SQLAlchemy Query Builder: Custom Query Examples

All custom queries live inside concrete repository methods. Each method opens its own session with `self.connection.get_session()`, builds a `select()` statement against the mapped table objects, and extracts results using `scalar_one_or_none()` (single result) or `scalars().all()` (list). Value objects used in `.where()` clauses are converted to their primitive representations automatically by the column's `TypeDecorator`.

---

## Single result — filter by column

Return one domain object or `None`. Use `scalar_one_or_none()` only when the filtered column is `unique`; if the query can match multiple rows it raises `MultipleResultsFound`.

```python
# order/infrastructure/persistence/order_repository.py
from sqlalchemy import select
from framework.infrastructure.persistence.repository import SQLAlchemyBaseRepository
from order.domain.order import Order
from order.domain.order_repository import OrderRepository
from order.domain.value.order_number import OrderNumber
from order.infrastructure.persistence.tables import orders_table

class SQLAlchemyOrderRepository(OrderRepository, SQLAlchemyBaseRepository):
    @property
    def entity(self) -> type[Order]:
        return Order

    def find_by_number(self, number: OrderNumber) -> Order | None:
        with self.connection.get_session() as session:
            return session.execute(
                select(Order).where(orders_table.c.number == number)
            ).scalar_one_or_none()
```

> **Notes:**
> - `orders_table.c.number == number` passes the `OrderNumber` value object directly. SQLAlchemy calls `process_bind_param` on the column's `TypeDecorator` to convert it to a plain string or integer before sending it to the database — no manual serialisation needed.
> - `scalar_one_or_none()` returns the mapped domain object directly, not a `Row` wrapper, so no further unpacking is needed.
> - If the column is not `unique`, replace `scalar_one_or_none()` with `scalars().first()` to return the first match without raising on duplicates, or `scalars().all()` to return every match.

---

## List result — filter with ordering and date range

Return multiple domain objects ordered by a timestamp column, filtered to a date window. Multiple arguments passed to `.where()` are combined with `AND`.

```python
# patients/infrastructure/persistence/vitals_repository.py
from datetime import datetime
from sqlalchemy import select
from ddd import Identity
from framework.infrastructure.persistence.repository import SQLAlchemyBaseRepository
from patients.domain.vitals import Vitals
from patients.domain.vitals_repository import VitalsRepository
from patients.infrastructure.persistence.tables import vitals_table

class SQLAlchemyVitalsRepository(VitalsRepository, SQLAlchemyBaseRepository):
    @property
    def entity(self) -> type[Vitals]:
        return Vitals

    def find_recent_by_patient(
        self, patient_id: Identity, since: datetime
    ) -> list[Vitals]:
        with self.connection.get_session() as session:
            return session.execute(
                select(Vitals)
                .where(
                    vitals_table.c.patient_id == patient_id,
                    vitals_table.c.recorded_at >= since,
                )
                .order_by(vitals_table.c.recorded_at.desc())
            ).scalars().all()
```

> **Notes:**
> - `scalars()` strips the `Row` wrapper and yields the ORM-mapped domain object directly; `.all()` materialises the cursor into a plain `list`.
> - Multiple positional arguments to `.where(...)` are joined with `AND`. Add further conditions the same way rather than stacking separate `.where()` calls.
> - `.order_by(col.desc())` sorts newest-first; swap to `.asc()` for oldest-first.
> - `since` is a plain `datetime` — `DateTime` columns have no `TypeDecorator`, so it passes through unchanged.
> - To cap the result set (e.g. the last 100 records), append `.limit(100)` to the `select()` expression.

---

## IN clause — bulk lookup by a list of values

Fetch all domain objects whose column value appears in a provided list. Common in query handlers that receive a set of IDs from the application layer.

```python
# patients/infrastructure/persistence/patient_repository.py
from sqlalchemy import select
from ddd import Identity
from framework.infrastructure.persistence.repository import SQLAlchemyBaseRepository
from patients.domain.patient import Patient
from patients.domain.patient_repository import PatientRepository
from patients.infrastructure.persistence.tables import patients_table

class SQLAlchemyPatientRepository(PatientRepository, SQLAlchemyBaseRepository):
    @property
    def entity(self) -> type[Patient]:
        return Patient

    def find_many(self, ids: list[Identity]) -> list[Patient]:
        with self.connection.get_session() as session:
            return session.execute(
                select(Patient).where(patients_table.c.id.in_(ids))
            ).scalars().all()
```

> **Notes:**
> - `.in_()` passes each element through the column's `TypeDecorator.process_bind_param` automatically — `Identity` value objects work directly without manual serialisation.
> - `.not_in()` is the inverse: rows whose column value is **not** in the list.
> - Passing an empty list produces `WHERE 1 != 1`, which returns no rows. This is safe and correct; no special-casing needed.
> - For large lists (thousands of IDs), prefer a subquery or a temporary table over a literal `IN` clause — most databases cap the number of bind parameters.

---

## EXISTS — check for related row presence

Determine whether at least one related row exists without loading the collection. More efficient than pulling a full list just to check `len() > 0`.

```python
# patients/infrastructure/persistence/patient_repository.py
from sqlalchemy import exists, select
from ddd import Identity
from framework.infrastructure.persistence.repository import SQLAlchemyBaseRepository
from patients.domain.patient import Patient
from patients.domain.patient_repository import PatientRepository
from patients.infrastructure.persistence.tables import patients_table, vitals_table

class SQLAlchemyPatientRepository(PatientRepository, SQLAlchemyBaseRepository):
    @property
    def entity(self) -> type[Patient]:
        return Patient

    def has_vitals(self, patient_id: Identity) -> bool:
        with self.connection.get_session() as session:
            return session.execute(
                select(exists().where(vitals_table.c.patient_id == patient_id))
            ).scalar_one()

    def find_with_vitals(self) -> list[Patient]:
        with self.connection.get_session() as session:
            return session.execute(
                select(Patient).where(
                    exists().where(vitals_table.c.patient_id == patients_table.c.id)
                )
            ).scalars().all()
```

> **Notes:**
> - `exists()` is imported from `sqlalchemy`.
> - **Standalone form** (`has_vitals`): wrapping `exists(...)` in `select()` returns a single-column, single-row result — `scalar_one()` extracts it as a plain `bool`.
> - **Filter form** (`find_with_vitals`): passing `exists(...)` to `.where()` on a domain-entity `select()` lets SQLAlchemy emit a correlated `WHERE EXISTS (SELECT 1 FROM vitals WHERE ...)` subquery and still return fully mapped `Patient` objects.
> - Prefer `EXISTS` over `COUNT > 0` when you only need a yes/no answer — the database can short-circuit after finding the first matching row.

---

## JOIN — filter by a related table's column

Return domain objects from one table filtered by a condition on a joined table. The canonical use case is finding parent aggregates that have at least one child row matching a criterion — here, all `Order` entities that contain a line for a given product.

```python
# order/infrastructure/persistence/order_repository.py
from sqlalchemy import select
from framework.infrastructure.persistence.repository import SQLAlchemyBaseRepository
from order.domain.order import Order
from order.domain.order_repository import OrderRepository
from order.infrastructure.persistence.tables import orders_table, order_lines_table

class SQLAlchemyOrderRepository(OrderRepository, SQLAlchemyBaseRepository):
    @property
    def entity(self) -> type[Order]:
        return Order

    def find_containing_product(self, product_name: str) -> list[Order]:
        with self.connection.get_session() as session:
            return session.execute(
                select(Order)
                .join(
                    order_lines_table,
                    order_lines_table.c.order_id == orders_table.c.id,
                )
                .where(order_lines_table.c.product_name == product_name)
            ).scalars().unique().all()
```

> **Notes:**
> - The `select()` target is always the entity you want back (`Order`). SQLAlchemy uses the join only to filter rows — the returned objects are fully mapped `Order` instances with their `_Order__lines` collection populated as configured in the mapper.
> - `.unique()` is required before `.all()` when a join can produce duplicate rows for the same aggregate (one `Order` with three matching lines appears three times in the raw result set). Without it you get repeated objects in the list.
> - This is an explicit column-level join — it does not use the ORM relationship defined in the mapper. Both forms produce the same SQL; the explicit form is clearer when the join condition is non-trivial.
> - Only join within the same aggregate boundary. Joining across aggregates (e.g. `orders_table` → `app_user`) couples bounded contexts at the query level. Resolve cross-aggregate reads through separate repository calls at the application layer instead.

---

## Aggregate SELECT — COUNT and AVG

Return a computed scalar rather than domain objects. Import `func` from `sqlalchemy` and pass column expressions to it; results come back as raw Python primitives.

```python
# patients/infrastructure/persistence/patient_repository.py
from datetime import datetime
from sqlalchemy import func, select
from ddd import Identity
from framework.infrastructure.persistence.repository import SQLAlchemyBaseRepository
from patients.domain.patient import Patient
from patients.domain.patient_repository import PatientRepository
from patients.infrastructure.persistence.tables import patients_table, vitals_table

class SQLAlchemyPatientRepository(PatientRepository, SQLAlchemyBaseRepository):
    @property
    def entity(self) -> type[Patient]:
        return Patient

    def count_born_before(self, cutoff: datetime) -> int:
        with self.connection.get_session() as session:
            return session.execute(
                select(func.count())
                .select_from(patients_table)
                .where(patients_table.c.date_of_birth <= cutoff)
            ).scalar_one()

    def average_heart_rate_for_patient(self, patient_id: Identity) -> float | None:
        with self.connection.get_session() as session:
            return session.execute(
                select(func.avg(vitals_table.c.heart_rate))
                .where(vitals_table.c.patient_id == patient_id)
            ).scalar_one()
```

> **Notes:**
> - `func.count()` with no argument counts all rows; `.select_from(table)` is required to tell SQLAlchemy which table to count from when no column is specified.
> - `func.avg(table.c.col)` infers its source table from the column reference — no `.select_from()` needed.
> - Both calls use `scalar_one()` (not `scalar_one_or_none()`) because aggregate functions always return exactly one row — even when no rows match, `COUNT` returns `0` and `AVG` returns `NULL` (mapped to Python `None`).
> - The return type of `func.avg(...)` is `float | None`: `None` when the `.where()` clause matches no rows. Callers should guard against this.
> - `func` also covers `func.sum(...)`, `func.min(...)`, `func.max(...)`, and any database-specific function — the pattern is identical.

---

## GROUP BY — grouped aggregates

Return one computed row per group rather than per entity. Results are raw `Row` tuples, not domain objects.

```python
# patients/infrastructure/persistence/patient_repository.py
from dataclasses import dataclass
from sqlalchemy import func, select
from ddd import Identity
from framework.infrastructure.persistence.repository import SQLAlchemyBaseRepository
from patients.domain.patient import Patient
from patients.domain.patient_repository import PatientRepository
from patients.infrastructure.persistence.tables import vitals_table

@dataclass(frozen=True)
class PatientHeartRateSummary:
    patient_id: Identity
    avg_heart_rate: float
    reading_count: int

class SQLAlchemyPatientRepository(PatientRepository, SQLAlchemyBaseRepository):
    @property
    def entity(self) -> type[Patient]:
        return Patient

    def heart_rate_summary_per_patient(self) -> list[PatientHeartRateSummary]:
        with self.connection.get_session() as session:
            rows = session.execute(
                select(
                    vitals_table.c.patient_id,
                    func.avg(vitals_table.c.heart_rate).label("avg_heart_rate"),
                    func.count().label("reading_count"),
                )
                .group_by(vitals_table.c.patient_id)
                .having(func.count() >= 3)
                .order_by(func.avg(vitals_table.c.heart_rate).desc())
            ).all()

            return [
                PatientHeartRateSummary(
                    patient_id=row.patient_id,
                    avg_heart_rate=row.avg_heart_rate,
                    reading_count=row.reading_count,
                )
                for row in rows
            ]
```

> **Notes:**
> - Results are `Row` named-tuples. `.label("name")` assigns a column alias that becomes the attribute name on the `Row` — without it you'd access columns by positional index.
> - `.having(func.count() >= 3)` filters groups after aggregation (SQL `HAVING`), as opposed to `.where()` which filters individual rows before grouping.
> - `GROUP BY` queries project across columns rather than loading aggregate roots — do not return raw `Row` objects from the repository. Map them to a plain `dataclass` (as shown) or a `dict` at the repository boundary so callers never depend on SQLAlchemy internals.
> - `vitals_table.c.patient_id` still goes through `IdentityType.process_result_value` when read back, so `row.patient_id` is an `Identity` value object, not a raw string.
