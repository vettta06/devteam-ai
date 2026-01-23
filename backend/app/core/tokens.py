from fastapi import HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.security import decode_jwt
from app.crud.token import get_refresh_token
from app.crud.user import get_user_by_id
from app.models.user import User
from app.schemas.token import TokenData


def get_token_from_request(request: Request) -> str:
    """Получает токен из заголовка Authorization."""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return auth_header[7:]


def verify_refresh_token(token: str, db: Session) -> User:
    """Проверяет refresh-токен и возвращает пользователя."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate refresh token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_jwt(token)
        user_id: str = payload.get("sub")
        token_type: str = payload.get("type")
        if user_id is None or token_type != "refresh":
            raise credentials_exception

        db_token = get_refresh_token(db, token)
        if db_token is None:
            raise credentials_exception

        from datetime import datetime, timezone

        if db_token.expires_at < datetime.now(timezone.utc):
            raise credentials_exception

        token_data = TokenData(user_id=int(user_id))
    except Exception as e:
        raise credentials_exception from e

    user = get_user_by_id(db, user_id=token_data.user_id)
    if user is None:
        raise credentials_exception
    return user
