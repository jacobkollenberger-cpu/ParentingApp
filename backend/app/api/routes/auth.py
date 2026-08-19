"""
Auth endpoints: register and login.

Security notes:
- Registration hashes the password before it ever touches the database -
  the plaintext password only exists in memory for this one request.
- Login deliberately returns the same generic error whether the email
  doesn't exist or the password is wrong - this avoids leaking which
  emails are registered (a common enumeration vulnerability).
- Tokens are short-lived JWTs signed with SECRET_KEY (see core/security.py).
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.schemas.auth import Token, UserCreate, UserLogin, UserResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user_in.email).first()
    if existing:
        # Generic detail on purpose - don't confirm which emails exist.
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not create account with provided details",
        )

    user = User(
        email=user_in.email,
        hashed_password=hash_password(user_in.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=Token)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    invalid_credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect email or password",
        headers={"WWW-Authenticate": "Bearer"},
    )

    user = db.query(User).filter(User.email == credentials.email).first()
    if user is None or not verify_password(credentials.password, user.hashed_password):
        raise invalid_credentials_exception

    if not user.is_active:
        raise invalid_credentials_exception

    access_token = create_access_token(data={"sub": str(user.id)})
    return Token(access_token=access_token)
