"""
Child access control.

This replaces the old `Child.owner_id == current_user.id` filter used
throughout the children routes. Access is now determined by an active
row in ChildMember, not by a single owner field.

`require_child_access` is a FastAPI dependency factory: call it with a
minimum required role tier to get a dependency that both verifies access
and hands back the child + membership row, so routes don't each
reimplement this lookup.

Deliberately NOT implemented yet (by design, see child_member.py):
- Per-entry authorship locking (whether one member can edit/delete
  another member's specific entries)
- The two-party medical-change approval workflow
- Custody-based permission overrides
These will layer on top of this access-check foundation later without
needing to change how routes call it.
"""

import uuid

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.child import Child
from app.models.child_member import PARENT_TIER_ROLES, STATUS_ACTIVE, ChildMember
from app.models.user import User


def get_child_membership(
    db: Session, child_id: uuid.UUID, user_id: uuid.UUID
) -> ChildMember | None:
    return (
        db.query(ChildMember)
        .filter(
            ChildMember.child_id == child_id,
            ChildMember.user_id == user_id,
            ChildMember.status == STATUS_ACTIVE,
        )
        .first()
    )


def require_child_access(require_parent_tier: bool = False):
    """Returns a dependency that verifies the current user has active
    access to the child in the path, and returns (child, membership).

    require_parent_tier=True restricts to PARENT/CO_PARENT roles - use
    this for actions a caregiver shouldn't be able to do (e.g. inviting
    new members, deleting the child profile).
    """

    def dependency(
        child_id: uuid.UUID,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
    ) -> tuple[Child, ChildMember]:
        child = db.query(Child).filter(Child.id == child_id).first()
        membership = get_child_membership(db, child_id, current_user.id)

        # Same 404 whether the child doesn't exist or the user just isn't
        # a member of it - don't leak which child_ids are real to someone
        # who isn't authorized to know.
        if child is None or membership is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Child not found")

        if require_parent_tier and membership.role not in PARENT_TIER_ROLES:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This action requires parent-level access",
            )

        return child, membership

    return dependency
