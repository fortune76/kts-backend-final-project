import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.users.models import UserModel


@pytest.fixture
async def user_1(
    db_sessionmaker: async_sessionmaker[AsyncSession],
) -> UserModel:
    new_user = UserModel(
        telegram_id=1223,
        nickname="aaa",
        first_name="bbb",
    )
    async with db_sessionmaker() as session:
        session.add(new_user)
        await session.commit()

    return new_user


@pytest.fixture
async def user_2(
    db_sessionmaker: async_sessionmaker[AsyncSession],
) -> UserModel:
    new_user = UserModel(
        telegram_id=321,
        nickname="ccc",
        first_name="ddd",
    )
    async with db_sessionmaker() as session:
        session.add(new_user)
        await session.commit()

    return new_user
