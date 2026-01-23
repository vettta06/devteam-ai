from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import decode_jwt, oauth2_scheme
from app.crud.user import get_user_by_id
from app.database import get_db
from app.models.user import User
from app.schemas.token import TokenData


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> User:
    """Получение текущего пользователя из JWT-токена."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_jwt(token)
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        token_data = TokenData(user_id=int(user_id))
    except Exception as e:
        raise credentials_exception from e

    user = get_user_by_id(db, user_id=token_data.user_id)
    if user is None:
        raise credentials_exception
    return user


def get_current_admin_user(cur_user: User = Depends(get_current_user)) -> User:
    """Проверка, что текущий пользователь - админ."""
    if not cur_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )
    return cur_user
