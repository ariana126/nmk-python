from sqlalchemy import Table, Column, String, DateTime, Index

from framework.infrastructure.persistence.mapper import mapper_registry
from framework.infrastructure.persistence.types import IdentityType, EmailType

users_table = Table(
    "app_user",
    mapper_registry.metadata,
    Column("id", IdentityType, primary_key=True),
    Column("email", EmailType, nullable=False, unique=True),
    Column("first_name", String, nullable=False),
    Column("last_name", String, nullable=False),
    Column("password", String, nullable=False),
    Column("registered_at", DateTime(timezone=True), nullable=False),
    Index("ix_app_user_email", "email"),
)
