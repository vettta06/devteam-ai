from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.auth import get_current_admin_user, get_current_user
from app.crud.user import (
    create_user,
    delete_user,
    get_all_users,
    get_user_by_email,
    update_user,
)
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserList, UserRead, UserUpdate

user_router = APIRouter()


@user_router.get("/me", response_model=UserRead)
async def read_users_me(cur_user: User = Depends(get_current_user)):
    """Получение информации о пользователе."""
    return UserRead.from_orm(cur_user)


@user_router.post("/", response_model=UserRead)
async def create_user_endpoint(
    user: UserCreate, db: Session = Depends(get_db)
) -> UserRead:
    """Создание пользователя."""
    try:
        return create_user(db=db, user=user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e


@user_router.get("/{email}", response_model=UserRead)
async def get_user(email: str, db: Session = Depends(get_db)):
    db_user = get_user_by_email(db, email=email)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@user_router.put("/me", response_model=UserRead)
async def update_user_me(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Обновление профиля текущего пользователя."""
    try:
        updated_user = update_user(db, user_id=current_user.id, user_update=user_update)
        return UserRead.from_orm(updated_user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@user_router.get("/", response_model=list[UserList])
async def get_users(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """Получение списка всех пользователей."""
    users = get_all_users(db, skip=skip, limit=limit)
    return [UserList.from_orm(user) for user in users]


@user_router.delete("/{user_id}")
async def delete_user_endpoint(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
) -> dict:
    """Удаление пользователя по id."""
    success = delete_user(db, user_id=user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}
