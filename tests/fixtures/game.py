import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.game.models import (
    GameInventoryModel,
    GameModel,
    PlayerInventoryModel,
    PlayerModel,
    ShareModel,
)
from app.users.models import UserModel


@pytest.fixture
async def game_1(
    db_sessionmaker: async_sessionmaker[AsyncSession],
    freeze_t,
) -> GameModel:
    new_game = GameModel(
        chat_id=123,
        started_at=freeze_t,
        finish_at=None,
    )
    async with db_sessionmaker() as session:
        session.add(new_game)
        await session.commit()

    return new_game


@pytest.fixture
async def player(
    db_sessionmaker: async_sessionmaker[AsyncSession],
    user_1: UserModel,
    game_1: GameModel,
) -> PlayerModel:
    new_player = PlayerModel(
        balance=1000,
        user_id=user_1.id,
        game_id=game_1.id,
    )
    async with db_sessionmaker() as session:
        session.add(new_player)
        await session.commit()

    return new_player


@pytest.fixture
async def share_1(
    db_sessionmaker: async_sessionmaker[AsyncSession],
) -> ShareModel:
    new_share = ShareModel(
        name="Gazprom",
        start_price=100,
    )
    async with db_sessionmaker() as session:
        session.add(new_share)
        await session.commit()

    return new_share


@pytest.fixture
async def share_2(
    db_sessionmaker: async_sessionmaker[AsyncSession],
) -> ShareModel:
    new_share = ShareModel(
        name="Sberbank",
        start_price=130,
    )
    async with db_sessionmaker() as session:
        session.add(new_share)
        await session.commit()

    return new_share


@pytest.fixture
async def share_3(
    db_sessionmaker: async_sessionmaker[AsyncSession],
) -> ShareModel:
    new_share = ShareModel(
        name="Mechel",
        start_price=15,
    )
    async with db_sessionmaker() as session:
        session.add(new_share)
        await session.commit()

    return new_share


@pytest.fixture
async def game_inventory_1(
    db_sessionmaker: async_sessionmaker[AsyncSession],
    share_1,
    game_1,
) -> GameInventoryModel:
    new_game_share = GameInventoryModel(
        share_id=share_1.id,
        game_id=game_1.id,
        price=200,
    )
    async with db_sessionmaker() as session:
        session.add(new_game_share)
        await session.commit()

    return new_game_share


@pytest.fixture
async def game_inventory_2(
    db_sessionmaker: async_sessionmaker[AsyncSession],
    share_2,
    game_1,
) -> GameInventoryModel:
    new_game_share = GameInventoryModel(
        share_id=share_2.id,
        game_id=game_1.id,
        price=100,
    )
    async with db_sessionmaker() as session:
        session.add(new_game_share)
        await session.commit()

    return new_game_share


@pytest.fixture
async def player_inventory_1(
    db_sessionmaker: async_sessionmaker[AsyncSession],
    player,
    game_inventory_1,
) -> PlayerInventoryModel:
    new_player_inventory = PlayerInventoryModel(
        share_owner=player.id,
        share_id=game_inventory_1.share_id,
    )

    async with db_sessionmaker() as session:
        session.add(new_player_inventory)
        await session.commit()
    return new_player_inventory
