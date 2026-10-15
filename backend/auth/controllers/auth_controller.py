"""
Auth HTTP Controller.
Unpacks HTTP requests, coordinates with AuthService, and maps responses/exceptions.
"""
from fastapi import HTTPException, status, Header
from sqlalchemy.orm import Session

from backend.auth.services.auth_service import auth_service
from backend.auth.schemas.auth_schema import (
    UserRegisterRequest,
    UserLoginRequest,
    TokenResponse,
    UserProfileResponse
)
from backend.auth.models.user_model import User


class AuthController:
    @staticmethod
    def register(db: Session, req: UserRegisterRequest) -> UserProfileResponse:
        try:
            user = auth_service.register_user(db, req)
            token = auth_service.create_access_token({
                "sub": str(user.id),
                "email": user.email,
                "role": user.role.value
            })
            resp = UserProfileResponse.model_validate(user)
            resp.access_token = token
            return resp
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )

    @staticmethod
    def login(db: Session, req: UserLoginRequest) -> TokenResponse:
        user = auth_service.authenticate_user(db, req.email, req.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is inactive"
            )

        token = auth_service.create_access_token({
            "sub": str(user.id),
            "email": user.email,
            "role": user.role.value
        })

        return TokenResponse(
            access_token=token,
            role=user.role.value,
            user_id=user.id,
            email=user.email,
            full_name=user.full_name
        )

    @staticmethod
    def get_current_user(db: Session, authorization: str = Header(None)) -> User:
        """Extracts and verifies user from Authorization header."""
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing or invalid Authorization header",
                headers={"WWW-Authenticate": "Bearer"},
            )
        token = authorization.split(" ")[1]
        payload = auth_service.decode_token(token)
        if not payload or "sub" not in payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        user_id = int(payload["sub"])
        user = auth_service.get_user_by_id(db, user_id)
        if not user or not user.is_active:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found or inactive")
        return user


auth_controller = AuthController()
