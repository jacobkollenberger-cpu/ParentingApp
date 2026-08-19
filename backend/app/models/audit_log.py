"""
Audit log data model.

Security notes:
- Audit logs are append-only from the application's perspective - there
  are deliberately no update/delete routes for this table. A tampered or
  deleted audit trail is worse than no audit trail, since it creates false
  confidence.
- `user_id` is nullable to support logging failed login attempts where the
  email doesn't correspond to a real account - you still want a record
  that *someone* tried, even if you can't attribute it to a known user.
- This table itself contains no medical/sensitive child data, only
  metadata about access (who, what action, which record, when) - so it
  doesn't need field-level encryption the way `Child.medical_notes` does.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    # Nullable: a failed login attempt for a non-existent email has no
    # real user to attribute it to.
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )

    # e.g. "create", "read", "update", "delete", "login_success", "login_failure"
    action: Mapped[str] = mapped_column(String(50))

    # e.g. "children", "auth" - the type of resource acted on
    resource_type: Mapped[str] = mapped_column(String(50))

    # The specific record affected, if applicable (e.g. a child's id).
    # Nullable for actions like login that aren't tied to one record.
    resource_id: Mapped[str | None] = mapped_column(String(100), nullable=True)

    success: Mapped[bool] = mapped_column(Boolean, default=True)

    # Optional short context, e.g. "incorrect password" - never log
    # sensitive payload data (no medical notes, no passwords) here.
    detail: Mapped[str | None] = mapped_column(String(255), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
