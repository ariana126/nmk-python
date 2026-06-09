from dataclasses import dataclass

from ddd import DomainEvent, Identity


@dataclass(frozen=True)
class VitalsRecorded(DomainEvent):
    vitals_id: Identity
