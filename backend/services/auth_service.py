"""
Authentication & Authorization Service.
Handles PBKDF2 password hashing, JWT token lifecycle, and Role-Based Access Control (RBAC).
"""
import hmac
import hashlib
from datetime import datetime, timedelta
from typing import Optional, List
from jose import jwt, JWTError
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from backend.config import settings
from backend.database import get_db
from backend.models import User, UserRole

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login", auto_error=False)

SALT = "snitch_luxury_streetwear_salt"


def hash_password(password: str) -> str:
    """Derives PBKDF2-HMAC-SHA256 key from plain password."""
    key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), SALT.encode("utf-8"), 100000)
    return key.hex()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Constant-time verification preventing timing side-channel attacks."""
    candidate = hash_password(plain_password)
    return hmac.compare_digest(candidate, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Signs JWT claims with expiration."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> Optional[dict]:
    """Decodes and verifies signature of JWT token."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None


def get_current_user(token: Optional[str] = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Optional[User]:
    """
    Extracts authenticated user from Bearer token if present.
    Allows guest access if token is absent.
    """
    if not token:
        return None
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token missing subject claim")
    
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User account inactive or not found")
    return user


def require_auth(user: Optional[User] = Depends(get_current_user)) -> User:
    """Enforces that a user is actively authenticated."""
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required for this operation",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return user


def require_role(allowed_roles: List[str]):
    """Enforces Role-Based Access Control (RBAC)."""
    def role_checker(user: User = Depends(require_auth)) -> User:
        user_role_str = str(user.role.value if hasattr(user.role, 'value') else user.role).lower()
        clean_allowed = [r.lower() for r in allowed_roles]
        if user_role_str not in clean_allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Forbidden: Insufficient privileges. Required: {allowed_roles}"
            )
        return user
    return role_checker
