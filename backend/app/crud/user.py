from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas import UserCreate


def create_user(db: Session, user: UserCreate) -> User:
    """Создание пользователя."""
    pass


def get_user_by_email(db: Session, email: str) -> User | None:
    """Получение пользователя по email."""
    pass
