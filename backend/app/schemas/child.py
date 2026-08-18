"""
Pydantic schemas define what the API accepts and returns - separate
from the database model so we control exactly what's exposed.
"""

import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class ChildBase(BaseModel):
    first_name: str
    date_of_birth: date
    allergies: str | None = None
    medical_notes: str | None = None
    preferences: str | None = None


class ChildCreate(ChildBase):
    pass


class ChildUpdate(BaseModel):
    first_name: str | None = None
    allergies: str | None = None
    medical_notes: str | None = None
    preferences: str | None = None


class ChildResponse(ChildBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    owner_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
