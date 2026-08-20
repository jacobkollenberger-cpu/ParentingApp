"""
Schemas for child_members - viewing who has access to a child.
"""

import uuid
from datetime import datetime

from pydantic import BaseModel


class ChildMemberResponse(BaseModel):
    id: uuid.UUID
    child_id: uuid.UUID
    user_id: uuid.UUID
    role: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
