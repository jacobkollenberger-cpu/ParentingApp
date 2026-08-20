"""
Schemas for child invitations.
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, field_validator

from app.models.child_member import ROLE_CAREGIVER, ROLE_CO_PARENT, ROLE_PARENT

VALID_INVITE_ROLES = {ROLE_PARENT, ROLE_CO_PARENT, ROLE_CAREGIVER}


class ChildInvitationCreate(BaseModel):
    invited_email: EmailStr
    role: str

    @field_validator("role")
    @classmethod
    def role_must_be_valid(cls, v: str) -> str:
        if v not in VALID_INVITE_ROLES:
            raise ValueError(f"role must be one of {sorted(VALID_INVITE_ROLES)}")
        return v


class ChildInvitationResponse(BaseModel):
    id: uuid.UUID
    child_id: uuid.UUID
    invited_email: str
    role: str
    status: str
    expires_at: datetime
    created_at: datetime
    # Included on creation so it can be shared as a link. Real email
    # delivery isn't wired up yet - see the route docstring.
    token: str | None = None

    class Config:
        from_attributes = True


class ChildInvitationAccept(BaseModel):
    token: str
