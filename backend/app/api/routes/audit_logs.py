"""
Audit log endpoint.

Read-only by design - there is no create/update/delete route for audit
logs. Entries are written exclusively by log_action() as a side effect of
other operations, never directly by a client.

Scoped to the current user's own entries, same ownership pattern as
/children - a real admin-review view across all users would need a
separate elevated role, which doesn't exist yet in this single-owner
model.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.audit_log import AuditLog
from app.models.user import User
from app.schemas.audit_log import AuditLogResponse

router = APIRouter(prefix="/audit-logs", tags=["audit"])


@router.get("/", response_model=list[AuditLogResponse])
def list_my_audit_logs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = 100,
):
    return (
        db.query(AuditLog)
        .filter(AuditLog.user_id == current_user.id)
        .order_by(AuditLog.created_at.desc())
        .limit(min(limit, 500))
        .all()
    )
