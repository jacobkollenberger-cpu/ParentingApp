"""
Audit logging helper.

Keeping this as a single function means every route logs in exactly the
same shape, and if the logging strategy ever changes (e.g. writing to a
separate append-only store instead of the main database), there's one
place to change it.
"""

import uuid

from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


def log_action(
    db: Session,
    action: str,
    resource_type: str,
    user_id: uuid.UUID | None = None,
    resource_id: str | None = None,
    success: bool = True,
    detail: str | None = None,
) -> None:
    """Write an audit log entry and commit it immediately.

    Called *after* the operation it's recording has already succeeded or
    failed, using the same DB session - so call this once you already
    know the outcome, not before.
    """
    entry = AuditLog(
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=str(resource_id) if resource_id is not None else None,
        success=success,
        detail=detail,
    )
    db.add(entry)
    db.commit()
