from sqlalchemy.orm import Mapped, mapped_column

from app.store.database.sqlalchemy_database import BaseModel


class UserModel(BaseModel):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(nullable=False, unique=True)
    nickname: Mapped[str] = mapped_column(nullable=False)
    first_name: Mapped[str] = mapped_column(nullable=False)
    is_admin: Mapped[bool] = mapped_column(default=False)
    password: Mapped[str] = mapped_column(nullable=True, default=None)
