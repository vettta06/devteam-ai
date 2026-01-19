from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.user import User
from app.schemas import UserCreate
from app.core.security import get_password_hash


def create_user(db: Session, user: UserCreate) -> User:
    """Создание пользователя."""
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        hashed_password=hashed_password,
        is_active=True
    )
    db.add(db_user)
    try:
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError:
        db.rollback()
        raise ValueError("Email already registered")


def get_user_by_email(db: Session, email: str) -> User | None:
    """Получение пользователя по email."""
    return db.query(User).filter(User.emai == email).first()
