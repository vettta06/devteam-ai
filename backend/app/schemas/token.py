from pydantic import BaseModel


class Token(BaseModel):
    """Модель для ответа клиенту."""

    access_token: str
    refresh_token: str
    token_type: str


class TokenData(BaseModel):
    """Модель для данных в JWT."""

    user_id: int | None = None
