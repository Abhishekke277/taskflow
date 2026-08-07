from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from backend.database import get_db
from backend.models.user import User
from backend.schemas.auth import UserRegister, UserLogin, TokenResponse
from backend.auth.security import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=201)
def register(payload: UserRegister, db: Session = Depends(get_db)):
    """
    Creates a new user account with a securely hashed password,
    then immediately logs them in by returning an access token —
    so the user goes straight from registering into the app.
    """
    new_user = User(
        name=payload.name,
        email=payload.email,
        hashed_password=hash_password(payload.password),
    )

    db.add(new_user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="An account with this email already exists.")

    db.refresh(new_user)

    token = create_access_token(new_user.id)
    return TokenResponse(
        access_token=token,
        user_id=new_user.id,
        name=new_user.name,
        email=new_user.email,
    )


@router.post("/login", response_model=TokenResponse)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    """
    Verifies email + password against the stored hash.
    Returns an access token on success.
    """
    user = db.query(User).filter(User.email == payload.email).first()

    if user is None or not verify_password(payload.password, user.hashed_password):
        # Deliberately the same error for "no such email" and "wrong
        # password" — this prevents attackers from figuring out which
        # emails are registered by testing different addresses.
        raise HTTPException(status_code=401, detail="Incorrect email or password.")

    token = create_access_token(user.id)
    return TokenResponse(
        access_token=token,
        user_id=user.id,
        name=user.name,
        email=user.email,
    )