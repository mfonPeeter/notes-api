from typing import Annotated
from datetime import datetime, timezone
import logging
from sqlmodel import select
from sqlalchemy.exc import MultipleResultsFound
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.database import SessionDep
from .schemas import (
    AuthResponse,
    UserCreate,
    User,
    UserPublic,
    UserUpdate,
    UserPasswordUpdate,
)
from .utils import get_password_hash, create_access_token, verify_password
from .dependencies import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])


@router.post(
    "/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED
)
async def register(payload: UserCreate, session: SessionDep):
    try:
        existing_user = session.exec(
            select(User).where(User.email == payload.email)
        ).one_or_none()
    except MultipleResultsFound as e:
        logger.exception(f"Data integrity error during registration: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Data integrity error",
        )

    if existing_user:
        logger.warning(f"Registration attempt with existing email: {payload.email}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email is already registered",
        )

    hashed_password = get_password_hash(payload.password)
    user = User(
        **payload.model_dump(exclude={"password"}),
        password=hashed_password,
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    logger.info(f"New user registered: {user.email}")
    access_token = create_access_token(data={"sub": user.email})
    return AuthResponse(access_token=access_token, user=user)


@router.post("/login", response_model=AuthResponse)
async def login(
    payload: Annotated[OAuth2PasswordRequestForm, Depends()], session: SessionDep
):
    try:
        user = session.exec(
            select(User).where(User.email == payload.username)
        ).one_or_none()
    except MultipleResultsFound as e:
        logger.exception(f"Data integrity error during login: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Data integrity error",
        )

    if not (user and verify_password(payload.password, user.password)):
        logger.warning(f"Failed login attempt for: {payload.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid login credentials"
        )

    logger.info(f"User logged in: {user.email}")
    access_token = create_access_token(data={"sub": user.email})
    return AuthResponse(access_token=access_token, user=user)


@router.patch("/me", response_model=UserPublic)
async def update_me(
    payload: UserUpdate,
    session: SessionDep,
    current_user: User = Depends(get_current_user),
):
    user_data = payload.model_dump(exclude_unset=True)
    user_data["updated_at"] = datetime.now(timezone.utc)
    current_user.sqlmodel_update(user_data)
    session.add(current_user)
    session.commit()
    session.refresh(current_user)

    logger.info(f"User {current_user.id} updated their profile")
    return current_user


@router.patch("/me/update-password")
async def update_password(
    payload: UserPasswordUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    session: SessionDep,
):
    if not verify_password(payload.current_password, current_user.password):
        logger.warning(f"Failed password update attempt for user: {current_user.id}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password"
        )

    current_user.sqlmodel_update(
        {
            "password": get_password_hash(payload.new_password),
            "updated_at": datetime.now(timezone.utc),
        }
    )
    session.add(current_user)
    session.commit()

    logger.info(f"User {current_user.id} updated their password")
    return {"message": "Password updated successfully"}


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_me(
    current_user: Annotated[User, Depends(get_current_user)], session: SessionDep
):
    logger.info(f"User {current_user.id} deleted their account")
    session.delete(current_user)
    session.commit()
