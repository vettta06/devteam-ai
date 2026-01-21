from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import get_password_hash, verify_password
from app.models.user import User
from app.schemas import UserCreate, UserUpdate


def create_user(db: Session, user: UserCreate) -> User:
    """Создание пользователя."""
    hashed_password = get_password_hash(user.password)
    db_user = User(email=user.email, hashed_password=hashed_password, is_active=True)
    db.add(db_user)
    try:
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError as e:
        db.rollback()
        raise ValueError("Email already registered") from e


def get_user_by_email(db: Session, email: str) -> User | None:
    """Получение пользователя по email."""
    return db.query(User).filter(User.email == email).first()


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    """Аутентификация."""
    user = get_user_by_email(db, email=email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def get_user_by_id(db: Session, user_id: int) -> User | None:
    """Получение пользователя по id."""
    user = db.query(User).filter(User.id == user_id).first()
    return user


def update_user(db: Session, user_id: int, user_update: UserUpdate) -> User:
    """Обновление пользователя."""
    db_user = get_user_by_id(db, user_id=user_id)
    if not db_user:
        raise ValueError("User not found")
    if user_update.email:
        db_user.email = user_update.email
    if user_update.password:
        db_user.hashed_password = get_password_hash(user_update.password)
    db.commit()
    db.refresh(db_user)
    return db_user
