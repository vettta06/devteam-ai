from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.crud.user import get_user_by_confirmation_token
from app.database import get_db

email_router = APIRouter()


@email_router.get("/confirm-email/{token}")
async def confirm_email(token: str, db: Session = Depends(get_db)):
    """Подтверждение email по токену."""
    user = get_user_by_confirmation_token(db, token)
    if not user:
        raise HTTPException(status_code=404, detail="Invalid or expired token")
    user.is_active = True
    user.confirmation_token = None
    db.commit()
    return {"message": "Email confirmed successfully!"}
