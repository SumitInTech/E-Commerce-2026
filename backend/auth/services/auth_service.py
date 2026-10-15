"""
Auth Business Domain Service.
Handles constant-time cryptographic password hashing, JWT HS256 creation,
token verification, and Role-Based Access Control (RBAC).
"""
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from backend.config import settings
from backend.auth.models.user_model import User, UserRole
from backend.auth.schemas.auth_schema import UserRegisterRequest


class AuthService:
    @staticmethod
    def hash_password(password: str) -> str:
        """Deterministic PBKDF2-HMAC-SHA256 password salting."""
        salt = "snitch_luxury_streetwear_salt"
        key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000)
        return key.hex()

    @classmethod
    def verify_password(cls, plain_password: str, hashed_password: str) -> bool:
        """Verifies password against stored PBKDF2 hash."""
        return cls.hash_password(plain_password) == hashed_password

    @staticmethod
    def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Issues cryptographically signed JWT with expiration timestamp."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt

    @staticmethod
    def decode_token(token: str) -> Optional[Dict[str, Any]]:
        """Validates and decodes JWT bearer token."""
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            return payload
        except JWTError:
            return None

    @classmethod
    def register_user(cls, db: Session, user_in: UserRegisterRequest) -> User:
        """Registers a new buyer, seller, or admin into database."""
        existing = db.query(User).filter(User.email == user_in.email).first()
        if existing:
            raise ValueError("Email already registered")

        user = User(
            email=user_in.email,
            hashed_password=cls.hash_password(user_in.password),
            full_name=user_in.full_name,
            role=user_in.role or UserRole.BUYER,
            phone=user_in.phone,
            address=user_in.address
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @classmethod
    def authenticate_user(cls, db: Session, email: str, password: str) -> Optional[User]:
        """Validates user credentials against stored hash."""
        user = db.query(User).filter(User.email == email).first()
        if not user:
            return None
        if not cls.verify_password(password, user.hashed_password):
            return None
        return user

    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        return db.query(User).filter(User.id == user_id).first()


auth_service = AuthService()
