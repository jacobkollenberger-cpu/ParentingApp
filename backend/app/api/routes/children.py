"""
Child profile endpoints.

Access control: now based on ChildMember rows, not a single owner_id -
see app/core/child_access.py. Every read/write requires an active
membership on the child in question; create/invite-adjacent actions
additionally require a parent-tier role.

Every read and write is audit-logged, including failed access attempts -
those failures are exactly what you'd review to spot someone probing for
records they don't have access to.
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.core.audit import log_action
from app.core.child_access import require_child_access
from app.models.child import Child
from app.models.child_member import ROLE_PARENT, STATUS_ACTIVE, ChildMember
from app.models.user import User
from app.schemas.child import ChildCreate, ChildResponse, ChildUpdate

router = APIRouter(prefix="/children", tags=["children"])


@router.post("/", response_model=ChildResponse, status_code=status.HTTP_201_CREATED)
def create_child(
    child_in: ChildCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # owner_id retained as a "who originally created this" reference, but
    # is no longer what access control checks against - see child_access.py.
    child = Child(**child_in.model_dump(), owner_id=current_user.id)
    db.add(child)
    db.flush()  # get child.id before creating the membership row

    membership = ChildMember(
        child_id=child.id,
        user_id=current_user.id,
        role=ROLE_PARENT,
        status=STATUS_ACTIVE,
    )
    db.add(membership)
    db.commit()
    db.refresh(child)

    log_action(
        db, action="create", resource_type="children",
        user_id=current_user.id, resource_id=child.id,
    )
    return child


@router.get("/", response_model=list[ChildResponse])
def list_children(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    children = (
        db.query(Child)
        .join(ChildMember, ChildMember.child_id == Child.id)
        .filter(ChildMember.user_id == current_user.id, ChildMember.status == STATUS_ACTIVE)
        .all()
    )
    log_action(
        db, action="read", resource_type="children",
        user_id=current_user.id, detail=f"listed {len(children)} record(s)",
    )
    return children


@router.get("/{child_id}", response_model=ChildResponse)
def get_child(
    access: tuple = Depends(require_child_access()),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    child, _membership = access
    log_action(
        db, action="read", resource_type="children",
        user_id=current_user.id, resource_id=child.id,
    )
    return child


@router.patch("/{child_id}", response_model=ChildResponse)
def update_child(
    child_in: ChildUpdate,
    access: tuple = Depends(require_child_access()),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # NOTE: this currently lets any active member (including caregivers)
    # update any field, including allergies/medical_notes. The two-party
    # approval workflow for sensitive fields, and per-role field
    # restrictions, are intentionally not built yet - see child_member.py.
    child, _membership = access

    updated_fields = list(child_in.model_dump(exclude_unset=True).keys())
    for field, value in child_in.model_dump(exclude_unset=True).items():
        setattr(child, field, value)

    db.commit()
    db.refresh(child)

    log_action(
        db, action="update", resource_type="children",
        user_id=current_user.id, resource_id=child.id,
        detail=f"fields: {', '.join(updated_fields)}" if updated_fields else None,
    )
    return child


@router.delete("/{child_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_child(
    access: tuple = Depends(require_child_access(require_parent_tier=True)),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    child, _membership = access
    db.delete(child)
    db.commit()

    log_action(
        db, action="delete", resource_type="children",
        user_id=current_user.id, resource_id=child.id,
    )
