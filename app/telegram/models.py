from sqlalchemy import BigInteger, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.store.database.sqlalchemy_database import BaseModel


class PollModel(BaseModel):
    __tablename__ = "polls"
    poll_id: Mapped[str] = mapped_column(primary_key=True, nullable=False)
    game_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("games.id"), nullable=False
    )
