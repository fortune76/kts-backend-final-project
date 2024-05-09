from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.store import Store
from app.users.models import UserModel
from app.web.config import Config
from tests.utils import user_to_dict


class TestUserAccessor:
    async def test_table_exists(self, inspect_list_tables: list[str]):
        assert "users" in inspect_list_tables

    async def test_create_user(
        self,
        db_sessionmaker: async_sessionmaker[AsyncSession],
        store: Store,
    ):
        user = await store.user.create_user(
            993,
            "zxc",
            "gul",
        )

        assert isinstance(user, UserModel)

        async with db_sessionmaker() as session:
            db_user = await session.scalar(
                select(UserModel).where(UserModel.telegram_id == 993)
            )

        assert user_to_dict(db_user) == {
            "id": 2,
            "telegram_id": 993,
            "nickname": "zxc",
            "first_name": "gul",
            "is_admin": False,
            "password": None,
        }

        # TODO: сделать тест для админа

    async def test_create_admin_on_startup(
        self,
        db_sessionmaker: async_sessionmaker[AsyncSession],
        store: Store,
        config: Config,
    ):
        admin_user = await store.user.get_admin_by_telegram_id(
            config.admin.telegram_id
        )
        assert isinstance(admin_user, UserModel)
        assert admin_user.password != store.app.config.admin.password
        assert admin_user.id == 1

    async def test_get_admin_by_telegram_id(
        self,
        db_sessionmaker: async_sessionmaker[AsyncSession],
        store: Store,
    ):
        user_admin = await store.user.get_admin_by_telegram_id(123)
        assert isinstance(user_admin, UserModel)
        assert user_admin.telegram_id == 123

    async def test_user_is_admin(
        self,
        db_sessionmaker: async_sessionmaker[AsyncSession],
        store: Store,
        config: Config,
    ):
        user_admin = await store.user.is_admin(123)
        assert user_admin is True

        user_is_not_admin = await store.user.is_admin(333)
        assert user_is_not_admin is False
