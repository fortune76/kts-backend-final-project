import datetime

from sqlalchemy import DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.store.database.sqlalchemy_database import BaseModel


class PlayerModel(BaseModel):
    __tablename__ = "players"
    id: Mapped[int] = mapped_column(
        primary_key=True, autoincrement=True, init=False
    )
    balance: Mapped[int] = mapped_column()
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    game_id: Mapped[int] = mapped_column(
        ForeignKey("games.id", ondelete="CASCADE"), nullable=False
    )
    alive: Mapped[bool] = mapped_column(default=True)


class ShareModel(BaseModel):
    __tablename__ = "shares"
    id: Mapped[int] = mapped_column(
        primary_key=True, autoincrement=True, init=False
    )
    name: Mapped[str] = mapped_column(nullable=False)
    start_price: Mapped[int] = mapped_column(default=0)


class GameInventoryModel(BaseModel):
    __tablename__ = "game_inventory"
    share_id: Mapped[int] = mapped_column(
        ForeignKey("shares.id", ondelete="CASCADE"),
        nullable=False,
        primary_key=True,
    )
    game_id: Mapped[int] = mapped_column(
        ForeignKey("games.id", ondelete="CASCADE"), nullable=False
    )
    price: Mapped[int] = mapped_column(default=0)


class GameModel(BaseModel):
    __tablename__ = "games"
    id: Mapped[int] = mapped_column(
        primary_key=True, autoincrement=True, init=False
    )
    chat_id: Mapped[int] = mapped_column(nullable=False)
    started_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=False), nullable=False
    )
    finish_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=False), nullable=True
    )
    is_active: Mapped[bool] = mapped_column(default=True)
    last_turn: Mapped[int] = mapped_column(default=0)


class PlayerInventoryModel(BaseModel):
    __tablename__ = "player_inventory"
    id: Mapped[int] = mapped_column(
        primary_key=True, autoincrement=True, init=False
    )
    share_id: Mapped[int] = mapped_column(
        ForeignKey("game_inventory.share_id", ondelete="CASCADE"),
        nullable=False,
    )
    share_owner: Mapped[int] = mapped_column(
        ForeignKey("players.id", ondelete="CASCADE"), nullable=False
    )
