from dataclasses import dataclass

from ddd import DomainEvent, Identity

@dataclass
class PatientRegistered(DomainEvent):
    patient_id: Identity
