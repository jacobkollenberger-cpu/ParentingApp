"""
Child membership and invitation endpoints.

Note on email delivery: this does NOT actually send an email yet. The
invitation is created and its token/link returned directly in the API
response, which is fine for development/demo but not for real use -
before this is user-facing, sending the link via a real email provider
(e.g. SES, SendGrid, Postmark) needs to replace returning the raw token
to the inviter's own client. Flagging this explicitly rather than
quietly shipping something that looks done but isn't.
"""

import secrets
import uuid
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.core.audit import log_action
from app.core.child_access import get_child_membership, require_child_access
from app.models.child import Child
from app.models.child_invitation import STATUS_ACCEPTED, STATUS_PENDING, ChildInvitation
from app.models.child_member import STATUS_ACTIVE, ChildMember
from app.models.user import User
from app.schemas.child_invitation import (
    ChildInvitationAccept,
    ChildInvitationCreate,
    ChildInvitationResponse,
)
from app.schemas.child_member import ChildMemberResponse

router = APIRouter(tags=["child_members"])

INVITATION_EXPIRY_DAYS = 7


@router.get("/children/{child_id}/members", response_model=list[ChildMemberResponse])
def list_members(
    access: tuple[Child, ChildMember] = Depends(require_child_access()),
    db: Session = Depends(get_db),
):
    child, _membership = access
    return db.query(ChildMember).filter(ChildMember.child_id == child.id).all()


@router.post(
    "/children/{child_id}/invitations",
    response_model=ChildInvitationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_invitation(
    invite_in: ChildInvitationCreate,
    access: tuple[Child, ChildMember] = Depends(require_child_access(require_parent_tier=True)),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    child, _membership = access

    invitation = ChildInvitation(
        child_id=child.id,
        invited_email=invite_in.invited_email,
        invited_by_user_id=current_user.id,
        role=invite_in.role,
        token=secrets.token_urlsafe(32),
        status=STATUS_PENDING,
        expires_at=datetime.now(timezone.utc) + timedelta(days=INVITATION_EXPIRY_DAYS),
    )
    db.add(invitation)
    db.commit()
    db.refresh(invitation)

    log_action(
        db, action="invite_created", resource_type="child_invitations",
        user_id=current_user.id, resource_id=invitation.id,
        detail=f"invited {invite_in.invited_email} as {invite_in.role}",
    )
    return invitation


@router.post("/invitations/accept", response_model=ChildMemberResponse)
def accept_invitation(
    accept_in: ChildInvitationAccept,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    invitation = (
        db.query(ChildInvitation)
        .filter(ChildInvitation.token == accept_in.token)
        .first()
    )

    if invitation is None or invitation.status != STATUS_PENDING:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or already-used invitation")

    if invitation.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This invitation has expired")

    # Deliberately not checking that current_user.email matches
    # invited_email - requiring an exact match is a product decision you
    # may want later (it would prevent someone else with the link from
    # accepting), but isn't enforced yet.

    existing = get_child_membership(db, invitation.child_id, current_user.id)
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Already a member of this child")

    membership = ChildMember(
        child_id=invitation.child_id,
        user_id=current_user.id,
        role=invitation.role,
        status=STATUS_ACTIVE,
    )
    db.add(membership)

    invitation.status = STATUS_ACCEPTED
    db.commit()
    db.refresh(membership)

    log_action(
        db, action="invite_accepted", resource_type="child_members",
        user_id=current_user.id, resource_id=membership.id,
    )
    return membership
