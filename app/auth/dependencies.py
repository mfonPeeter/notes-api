from typing import Annotated

import jwt
import logging
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from sqlmodel import select

from app.config import settings
from app.database import SessionDep
from app.auth.schemas import User

logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)], session: SessionDep
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        email = payload.get("sub")
        if email is None:
            logger.warning(f"Token missing 'sub' claim")
            raise credentials_exception
    except InvalidTokenError:
        logger.warning(f"Invalid or expired token")
        raise credentials_exception

    user = session.exec(select(User).where(User.email == email)).first()
    if user is None:
        logger.warning(f"Authenticated user not found in database")
        raise credentials_exception

    logger.debug(f"Authenticated user: {user.email}")
    return user
