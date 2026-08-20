"""
Child invitations - the mechanism for adding a new member to a child's
profile without letting anyone just supply a child_id and grant themselves
access.

Flow:
1. An existing active member (with invite permission) creates an
   invitation for an email address + role.
2. A random, unguessable token is generated and (eventually) emailed as a
   link. Actual email delivery is not wired up yet - see note in the
   invite route - so for now the token/link is returned directly in the
   API response for manual sharing during demo/dev.
3. The invited person visits the link, logs in or registers, and calls
   the accept endpoint with the token.
4. On acceptance, a ChildMember row is created and the invitation is
   marked accepted. Tokens expire (see `expires_at`) so a stale, possibly
   leaked invite link can't be used indefinitely.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base

STATUS_PENDING = "pending"
STATUS_ACCEPTED = "accepted"
STATUS_EXPIRED = "expired"
STATUS_REVOKED = "revoked"


class ChildInvitation(Base):
    __tablename__ = "child_invitations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    child_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("children.id"), nullable=False
    )
    invited_email: Mapped[str] = mapped_column(String(255), nullable=False)
    invited_by_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    role: Mapped[str] = mapped_column(String(50), nullable=False)

    # Random URL-safe token, unique and unguessable - this is the actual
    # credential that grants the ability to accept the invite, so it's
    # generated with secrets.token_urlsafe, not a predictable ID.
    token: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)

    status: Mapped[str] = mapped_column(String(20), default=STATUS_PENDING)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
