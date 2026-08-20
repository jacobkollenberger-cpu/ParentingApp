"""
Child membership - who has access to a child's profile, and in what role.

This is the foundation for co-parenting: rather than a single owner_id on
Child, access is granted per-user via rows in this table. A child can have
multiple active members (parent, co-parent, caregiver); a user can belong
to multiple children.

Design notes on fields marked "reserved for later":
These columns exist now, unused by any logic yet, so the schema doesn't
need a disruptive migration when those features are actually built later.
Adding a nullable column today is cheap; retrofitting one onto a live
table with real relationships later is not.

- `custody_declared` / `custody_document_note`: for a future feature
  letting a parent self-declare primary legal custody, optionally
  referencing an uploaded document. Important: this would be a
  *self-declaration*, never independently verified by the system - the
  app has no way to confirm a court order's authenticity. That
  verification limitation should stay explicit in the UI whenever this
  is built, not just in this comment.
- `can_approve_medical_changes`: for a future approval-workflow feature
  where changes to sensitive fields (allergies, medical_notes) require
  confirmation from more than one active parent-tier member before
  taking effect, rather than any one parent unilaterally overwriting them.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base

# Role tier determines base permissions. Kept as plain strings (not a DB
# enum) so adding a role later is a code change, not a migration.
ROLE_PARENT = "parent"
ROLE_CO_PARENT = "co_parent"
ROLE_CAREGIVER = "caregiver"

PARENT_TIER_ROLES = {ROLE_PARENT, ROLE_CO_PARENT}

STATUS_ACTIVE = "active"
STATUS_PENDING = "pending"
STATUS_REMOVED = "removed"


class ChildMember(Base):
    __tablename__ = "child_members"
    __table_args__ = (
        # A user can only have one membership row per child - prevents
        # duplicate/conflicting role assignments for the same pairing.
        UniqueConstraint("child_id", "user_id", name="uq_child_member"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    child_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("children.id"), nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )

    role: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default=STATUS_ACTIVE)

    # --- Reserved for later (see module docstring) ---
    custody_declared: Mapped[bool] = mapped_column(Boolean, default=False)
    custody_document_note: Mapped[str | None] = mapped_column(String(255), nullable=True)
    can_approve_medical_changes: Mapped[bool] = mapped_column(Boolean, default=True)
    # ---------------------------------------------------

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
