import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey
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
        BigInteger, ForeignKey("games.id", ondelete="CASCADE"), nullable=False
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
    id: Mapped[int] = mapped_column(
        primary_key=True, autoincrement=True, init=False
    )
    share_id: Mapped[int] = mapped_column(
        ForeignKey("shares.id", ondelete="CASCADE"),
        nullable=False,
    )
    game_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("games.id", ondelete="CASCADE"),
        nullable=False,
    )
    price: Mapped[int] = mapped_column(default=0)


class GameModel(BaseModel):
    __tablename__ = "games"
    id: Mapped[int] = mapped_column(
        primary_key=True, autoincrement=True, init=False
    )
    chat_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
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
        ForeignKey("game_inventory.id", ondelete="CASCADE"),
        nullable=False,
    )
    share_owner: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("players.id", ondelete="CASCADE"), nullable=False
    )

class GameSettingsModel(BaseModel):
    __tablename__ = "game_settings"
    id: Mapped[int] = mapped_column(
        primary_key=True, autoincrement=True, init=False
    )
    turn_timer: Mapped[int] = mapped_column(default=30)
    turn_counter: Mapped[int] = mapped_column(default=5)
    player_balance: Mapped[int] = mapped_column(default=1000)
    shares_minimal_price: Mapped[int] = mapped_column(default=1)
    shares_maximum_price: Mapped[int] = mapped_column(default=500)