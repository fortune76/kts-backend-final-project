import os
import typing
from hashlib import sha256

from app.web.app import Application

if typing.TYPE_CHECKING:
    from app.web.app import Application

from sqlalchemy import and_, select

from app.base.base_accessor import BaseAccessor
from app.users.models import UserModel


class UserAccessor(BaseAccessor):
    async def connect(self, app: "Application"):
        config_admin = self.app.config.admin
        admin = await self.get_admin_by_telegram_id(int(os.getenv(config_admin.telegram_id)))
        if not admin:
            await self.create_admin(
                telegram_id=int(os.getenv(config_admin.telegram_id)),
                nickname=os.getenv(config_admin.nickname),
                first_name=os.getenv(config_admin.first_name),
                password=os.getenv(config_admin.password),
            )

    async def create_user(
        self, telegram_id: int, nickname: str, first_name: str
    ) -> UserModel:
        async with self.app.database.session() as session:
            user = UserModel(
                telegram_id=telegram_id,
                nickname=nickname,
                first_name=first_name,
            )
            session.add(user)
            await session.commit()
        return user

    async def get_user_by_id(self, id: int) -> UserModel | None:
        stmt = select(UserModel).where(UserModel.id == id)
        async with self.app.database.session() as session:
            user = await session.scalar(stmt)
        return user if user else None

    async def get_user_by_telegram_id(
        self, telegram_id: int
    ) -> UserModel | None:
        stmt = select(UserModel).where(UserModel.telegram_id == telegram_id)
        async with self.app.database.session() as session:
            user = await session.scalar(stmt)
        return user if user else None

    async def create_admin(
        self, telegram_id: int, nickname: str, first_name: str, password: str
    ) -> UserModel:
        admin_password = sha256(password.encode()).hexdigest()
        async with self.app.database.session() as session:
            user = UserModel(
                telegram_id=telegram_id,
                nickname=nickname,
                first_name=first_name,
                is_admin=True,
                password=admin_password,
            )
            session.add(user)
            await session.commit()

    async def get_admin_by_telegram_id(
        self, telegram_id: int
    ) -> UserModel | None:
        stmt = select(UserModel).where(
            and_(
                UserModel.telegram_id == telegram_id,
                UserModel.is_admin,
            )
        )
        async with self.app.database.session() as session:
            user = await session.scalar(stmt)
        return user if user else None

    async def is_admin(self, telegram_id: int) -> bool:
        stmt = select(UserModel).where(
            and_(
                UserModel.telegram_id == telegram_id,
                UserModel.is_admin,
            )
        )
        async with self.app.database.session() as session:
            user = await session.scalar(stmt)
        return bool(user)

    async def check_admin(self, telegram_id: int, password: str) -> bool:
        stmt = select(UserModel).where(
            and_(
                UserModel.telegram_id == telegram_id,
                UserModel.is_admin,
            )
        )
        async with self.app.database.session() as session:
            user = await session.scalar(stmt)
        return sha256(password.encode()).hexdigest() == user.password


    async def get_users_list(self) -> list[UserModel]:
        stmt = select(UserModel).order_by(UserModel.id)
        async with self.app.database.session() as session:
            return list(await session.scalars(stmt))
