from datetime import datetime

from sqlalchemy.orm import Session

from app.models.token import RefreshToken


def create_refresh_token(
    db: Session, user_id: int, token: str, expires_at: datetime
) -> RefreshToken:
    """Создание refresh-токена."""
    db_token = RefreshToken(user_id=user_id, token=token, expires_at=expires_at)
    db.add(db_token)
    db.commit()
    db.refresh(db_token)
    return db_token


def get_refresh_token(db: Session, token: str) -> RefreshToken:
    """Получение refresh-токена из базы данных."""
    return db.query(RefreshToken).filter(RefreshToken.token == token).first()


def delete_refresh_token(db: Session, token: str) -> None:
    """Удаляет токен из базы данных."""
    db_token = get_refresh_token(db, token)
    if db_token:
        db.delete(db_token)
        db.commit()
