"""
Child profile endpoints.

Access control: every query filters by owner_id == current_user.id.
This is deliberately simple for now (single-owner, no sharing yet) -
it's the seam where co-parenting permissions get added later without
restructuring anything else.
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.child import Child
from app.models.user import User
from app.schemas.child import ChildCreate, ChildResponse, ChildUpdate

router = APIRouter(prefix="/children", tags=["children"])


@router.post("/", response_model=ChildResponse, status_code=status.HTTP_201_CREATED)
def create_child(
    child_in: ChildCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    child = Child(**child_in.model_dump(), owner_id=current_user.id)
    db.add(child)
    db.commit()
    db.refresh(child)
    return child


@router.get("/", response_model=list[ChildResponse])
def list_children(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return db.query(Child).filter(Child.owner_id == current_user.id).all()


@router.get("/{child_id}", response_model=ChildResponse)
def get_child(
    child_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    child = (
        db.query(Child)
        .filter(Child.id == child_id, Child.owner_id == current_user.id)
        .first()
    )
    if child is None:
        # Deliberately identical error whether the child doesn't exist
        # or belongs to someone else - avoids leaking existence of records.
        raise HTTPException(status_code=404, detail="Child not found")
    return child


@router.patch("/{child_id}", response_model=ChildResponse)
def update_child(
    child_id: uuid.UUID,
    child_in: ChildUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    child = (
        db.query(Child)
        .filter(Child.id == child_id, Child.owner_id == current_user.id)
        .first()
    )
    if child is None:
        raise HTTPException(status_code=404, detail="Child not found")

    for field, value in child_in.model_dump(exclude_unset=True).items():
        setattr(child, field, value)

    db.commit()
    db.refresh(child)
    return child


@router.delete("/{child_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_child(
    child_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    child = (
        db.query(Child)
        .filter(Child.id == child_id, Child.owner_id == current_user.id)
        .first()
    )
    if child is None:
        raise HTTPException(status_code=404, detail="Child not found")

    db.delete(child)
    db.commit()
