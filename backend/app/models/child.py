"""
Child profile data model.

Security notes:
- `owner_id` ties every record to the parent account that created it -
  this is the foundation of access control (a parent can only ever
  query children they own or are explicitly shared with).
- Fields like `medical_notes` are flagged as sensitive in comments now;
  field-level encryption will wrap these before storage in a later pass.
"""

import uuid
from datetime import date, datetime, timezone

from sqlalchemy import Date, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.encryption import EncryptedString
from app.db.session import Base


class Child(Base):
    __tablename__ = "children"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    # Ownership - the parent account that created this profile.
    # RBAC checks in the API layer filter on this.
    owner_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))

    first_name: Mapped[str] = mapped_column(String(100))
    date_of_birth: Mapped[date] = mapped_column(Date)

    # SENSITIVE - encrypted at rest via EncryptedString (Fernet).
    # Note: encrypted columns can't be searched/filtered on in SQL - if a
    # future feature needs to query by allergy, that requires a separate
    # searchable/hashed index, not a wider SELECT on this column.
    allergies: Mapped[str | None] = mapped_column(EncryptedString, nullable=True)
    # SENSITIVE - encrypted at rest via EncryptedString (Fernet).
    medical_notes: Mapped[str | None] = mapped_column(EncryptedString, nullable=True)

    preferences: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
