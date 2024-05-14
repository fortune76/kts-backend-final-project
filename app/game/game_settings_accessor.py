from sqlalchemy import update, select

from app.base.base_accessor import BaseAccessor
from app.game.models import GameSettingsModel


class GameSettingsAccessor(BaseAccessor):
    async def get_turn_timer(self):
        stmt = select(GameSettingsModel.turn_timer).where(GameSettingsModel.id == 1)
        async with self.app.database.session() as session:
            return await session.scalar(stmt)

    async def update_turn_timer(self, turn_timer: int):
        stmt = update(GameSettingsModel).where(GameSettingsModel.id == 1).values(turn_timer=turn_timer)
        async with self.app.database.session() as session:
            await session.execute(stmt)

    async def get_turn_counter(self):
        stmt = select(GameSettingsModel.turn_counter).where(GameSettingsModel.id == 1)
        async with self.app.database.session() as session:
            return await session.scalar(stmt)

    async def update_turn_counter(self, turn_counter: int):
        stmt = update(GameSettingsModel).where(GameSettingsModel.id == 1).values(turn_counter=turn_counter)
        async with self.app.database.session() as session:
            await session.execute(stmt)

    async def get_player_balance(self):
        stmt = select(GameSettingsModel.player_balance).where(GameSettingsModel.id == 1)
        async with self.app.database.session() as session:
            return await session.scalar(stmt)

    async def update_player_balance(self, player_balance: int):
        stmt = update(GameSettingsModel).where(GameSettingsModel.id == 1).values(player_balance=player_balance)
        async with self.app.database.session() as session:
            await session.execute(stmt)

    async def get_shares_minimal_price(self):
        stmt = select(GameSettingsModel).where(GameSettingsModel.id == 1)
        async with self.app.database.session() as session:
            return await session.scalar(stmt)

    async def update_shares_minimal_price(self, shares_minimal_price: int):
        stmt = update(GameSettingsModel).where(GameSettingsModel.id == 1).values(
            shares_minimal_price=shares_minimal_price
        )
        async with self.app.database.session() as session:
            await session.execute(stmt)

    async def get_shares_maximum_price(self):
        stmt = select(GameSettingsModel).where(GameSettingsModel.id == 1)
        async with self.app.database.session() as session:
            return await session.scalar(stmt)

    async def update_shares_maximum_price(self, shares_maximum_price: int):
        stmt = update(GameSettingsModel).where(GameSettingsModel.id == 1).values(
            shares_maximum_price=shares_maximum_price
        )
        async with self.app.database.session() as session:
            await session.execute(stmt)