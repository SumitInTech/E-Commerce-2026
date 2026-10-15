"""
Auth API Router.
Registers HTTP endpoints for buyer, seller, and admin authentication workflows.
"""
from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session

from backend.database.supabase_client import get_db
from backend.auth.schemas.auth_schema import (
    UserRegisterRequest,
    UserLoginRequest,
    TokenResponse,
    UserProfileResponse
)
from backend.auth.controllers.auth_controller import auth_controller

router = APIRouter(prefix="/auth", tags=["Auth Service"])


@router.post("/register", response_model=UserProfileResponse)
def register(req: UserRegisterRequest, db: Session = Depends(get_db)):
    """Registers a new platform user."""
    return auth_controller.register(db, req)


@router.post("/login", response_model=TokenResponse)
def login(req: UserLoginRequest, db: Session = Depends(get_db)):
    """Authenticates credentials and returns cryptographically signed JWT."""
    return auth_controller.login(db, req)


@router.get("/me", response_model=UserProfileResponse)
def get_my_profile(authorization: str = Header(None), db: Session = Depends(get_db)):
    """Retrieves authenticated user profile based on Bearer token."""
    user = auth_controller.get_current_user(db, authorization)
    return UserProfileResponse.model_validate(user)
