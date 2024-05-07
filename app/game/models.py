from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.store.database.sqlalchemy_database import BaseModel


class PlayerModel(BaseModel):
    __tablename__ = "players"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    balance: Mapped[int] = mapped_column()
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    game_id: Mapped[int] = mapped_column(
        ForeignKey("games.id", ondelete="CASCADE"), nullable=False
    )
    alive: Mapped[int] = mapped_column(default=True)


class GameModel(BaseModel):
    __tablename__ = "games"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    chat_id: Mapped[int] = mapped_column(nullable=False)
    started_at: Mapped[str] = mapped_column(nullable=False)
    finish_at: Mapped[str] = mapped_column()
    is_active: Mapped[str] = mapped_column(default=True)
    last_turn: Mapped[str] = mapped_column(default=0)


class ShareModel(BaseModel):
    __tablename__ = "shares"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
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


class PlayerInventoryModel(BaseModel):
    __tablename__ = "player_inventory"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    share_id: Mapped[int] = mapped_column(
        ForeignKey("shares.id", ondelete="CASCADE"), nullable=False
    )
    share_owner: Mapped[int] = mapped_column(
        ForeignKey("players.id", ondelete="CASCADE"), nullable=False
    )
