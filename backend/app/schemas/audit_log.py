"""
Audit log response schema.
"""

import uuid
from datetime import datetime

from pydantic import BaseModel


class AuditLogResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID | None
    action: str
    resource_type: str
    resource_id: str | None
    success: bool
    detail: str | None
    created_at: datetime

    class Config:
        from_attributes = True
