import datetime

from dataclasses import dataclass
from sqlalchemy.orm import Mapped, relationship, mapped_column
from sqlalchemy import ForeignKey
from app.store.database.sqlalchemy_database import BaseModel

@dataclass
class Game:
    id: int
    chat_id: int
    is_active: bool
    last_turn: int
    started_at: datetime.datetime
    finish_at: datetime.datetime
    winner: int | None


@dataclass
class Player:
    id: int
    user_id: int
    balance: int
    game_id: int
    alive: bool


@dataclass
class Share:
    id: int
    name: str
    start_price: int


@dataclass
class GameInventory:
    share_id: int
    game_id: int
    price: int


@dataclass
class PlayerInventory:
    id: int
    share_id: int
    share_owner: int


class GameModel(BaseModel):
    __tablename__ = "games"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    chat_id: Mapped[int] = mapped_column(nullable=False)
    is_active: Mapped[str] = mapped_column(default=True)
    last_turn: Mapped[str] = mapped_column(default=0)
    started_at: Mapped[str] = mapped_column(nullable=False)
    finist_at: Mapped[str] = mapped_column()
    winner: Mapped[int] = mapped_column(ForeignKey("players.id", ondelete="CASCADE"), nullable=False)


class PlayerModel(BaseModel):
    __tablename__ = "players"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    balance: Mapped[int] = mapped_column()
    alive: Mapped[int] = mapped_column(default=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users,id", ondelete="CASCADE"), nullable=False)
    game_id: Mapped[int] = mapped_column(ForeignKey("games.id", ondelete="CASCADE"), nullable=False)


class ShareModel(BaseModel):
    __tablename__ = "shares"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(nullable=False)
    start_price: Mapped[int] = mapped_column(default=0)


class GameInventory(BaseModel):
    __tablename__ = "game_inventory"
    share_id: Mapped[int] = mapped_column(ForeignKey("shares.id", ondelete="CASCADE"), nullable=False)
    game_id: Mapped[int] = mapped_column(ForeignKey("games.id", ondelete="CASCADE"), nullable=False)
    price: Mapped[int] = mapped_column(default=0)


class PlayerInventory(BaseModel):
    __tablename__ = "player_inventory"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    share_id: Mapped[int] = mapped_column(ForeignKey("shares.id", ondelete="CASCADE"), nullable=False)
    share_owner: Mapped[int] = mapped_column(ForeignKey("players.id", ondelete="CASCADE"), nullable=False)
