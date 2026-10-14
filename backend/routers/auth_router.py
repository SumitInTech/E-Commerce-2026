"""
Auth Service Router.
Handles buyer, seller, and admin registration, credential login, and profile access.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import User, UserRole
from backend.schemas.auth import UserRegisterRequest, UserLoginRequest, TokenResponse, UserProfileResponse
from backend.services.auth_service import hash_password, verify_password, create_access_token, require_auth

router = APIRouter(prefix="/auth", tags=["2. Auth Service"])


@router.post("/register", response_model=TokenResponse)
def register(req: UserRegisterRequest, db: Session = Depends(get_db)):
    """Registers new buyer, seller, or admin and issues initial JWT token."""
    existing = db.query(User).filter(User.email == req.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address already exists."
        )

    role_val = UserRole.BUYER
    if req.role:
        try:
            role_val = UserRole(req.role.lower())
        except ValueError:
            role_val = UserRole.BUYER

    user = User(
        email=req.email,
        hashed_password=hash_password(req.password),
        full_name=req.full_name,
        role=role_val,
        phone=req.phone,
        address=req.address
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token({"sub": str(user.id), "email": user.email, "role": user.role.value})

    return TokenResponse(
        access_token=token,
        expires_in_minutes=1440,
        user_id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role.value
    )


@router.post("/login", response_model=TokenResponse)
def login(req: UserLoginRequest, db: Session = Depends(get_db)):
    """Validates user credentials and issues signed JWT bearer token."""
    user = db.query(User).filter(User.email == req.email).first()
    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password combination."
        )

    token = create_access_token({"sub": str(user.id), "email": user.email, "role": user.role.value})

    return TokenResponse(
        access_token=token,
        expires_in_minutes=1440,
        user_id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role.value
    )


@router.get("/me", response_model=UserProfileResponse)
def get_profile(current_user: User = Depends(require_auth)):
    """Retrieves profile of currently authenticated user."""
    return current_user
