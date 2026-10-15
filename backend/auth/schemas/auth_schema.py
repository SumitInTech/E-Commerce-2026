"""
Pydantic v2 Request & Response Data Transfer Objects (DTOs) for Auth Microservice.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from backend.auth.models.user_model import UserRole


class UserRegisterRequest(BaseModel):
    email: str = Field(..., pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$", description="Valid user email address")
    password: str = Field(..., min_length=6, description="Password min length 6")
    full_name: str = Field(..., min_length=2)
    role: Optional[UserRole] = UserRole.BUYER
    phone: Optional[str] = None
    address: Optional[str] = None


class UserLoginRequest(BaseModel):
    email: str = Field(..., pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$")
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    user_id: int
    email: str
    full_name: str


class UserProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    full_name: str
    role: UserRole
    phone: Optional[str] = None
    address: Optional[str] = None
    is_active: bool
    created_at: datetime
    access_token: Optional[str] = None
