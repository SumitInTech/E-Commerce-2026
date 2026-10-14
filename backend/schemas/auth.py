"""
Authentication & User Request/Response Schemas.
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class UserRegisterRequest(BaseModel):
    email: str = Field(..., description="User email address")
    password: str = Field(..., min_length=6, description="Minimum 6 characters")
    full_name: str
    role: Optional[str] = "buyer"  # buyer, seller, admin
    phone: Optional[str] = None
    address: Optional[str] = None


class UserLoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in_minutes: int
    user_id: int
    email: str
    full_name: str
    role: str


class UserProfileResponse(BaseModel):
    id: int
    email: str
    full_name: str
    role: str
    phone: Optional[str] = None
    address: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
