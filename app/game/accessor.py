import datetime

from sqlalchemy import and_, select

from app.base.base_accessor import BaseAccessor
from app.game.models import (
    GameInventoryModel,
    GameModel,
    PlayerInventoryModel,
    PlayerModel,
    ShareModel,
)


class GameAccessor(BaseAccessor):
    async def create_game(self, chat_id: int) -> GameModel:
        datetime_now = datetime.datetime.now()
        async with self.app.database.session() as session:
            game = GameModel(
                chat_id=chat_id,
                started_at=datetime_now,
                finish_at=None,
            )
            session.add(game)
            await session.commit()
        return game

    async def get_game_by_id(self, game_id: int) -> GameModel:
        stmt = select(GameModel).where(GameModel.id == game_id)
        async with self.app.database.session() as session:
            return await session.scalar(stmt)

    async def increase_game_turn(self, game_id: int) -> None:
        stmt = select(GameModel).where(GameModel.id == game_id)
        async with self.app.database.session() as session:
            game = await session.scalar(stmt)
            last_turn = game.last_turn + 1
            game.last_turn = last_turn
            await session.commit()

    async def finish_game(self, game_id: int) -> None:
        datetime_now = datetime.datetime.now()
        stmt = select(GameModel).where(GameModel.id == game_id)
        async with self.app.database.session() as session:
            game = await session.scalar(stmt)
            game.finish_at = datetime_now
            game.is_active = False
            await session.commit()

    async def create_player(
        self, user_id: int, balance: int, game_id: int
    ) -> PlayerModel:
        async with self.app.database.session() as session:
            player = PlayerModel(
                balance=balance,
                user_id=user_id,
                game_id=game_id,
            )
            session.add(player)
            await session.commit()
        return player

    async def get_player_by_id(self, player_id: int) -> PlayerModel:
        stmt = select(PlayerModel).where(PlayerModel.id == player_id)
        async with self.app.database.session() as session:
            return await session.scalar(stmt)

    async def get_player_balance(self, player_id: int) -> int:
        stmt = select(PlayerModel).where(PlayerModel.id == player_id)
        async with self.app.database.session() as session:
            return (await session.scalar(stmt)).balance

    async def update_player_balance(
        self, player_id: int, value: int, mode: str
    ) -> None:
        stmt = select(PlayerModel).where(PlayerModel.id == player_id)
        async with self.app.database.session() as session:
            player = await session.scalar(stmt)
            if mode == "increase":
                player.balance += value
            elif mode == "decrease":
                if player.balance >= value:
                    player.balance -= value
                else:
                    player.balance = 0
            await session.commit()

    async def player_dead(self, player_id: int) -> None:
        stmt = select(PlayerModel).where(PlayerModel.id == player_id)
        async with self.app.database.session() as session:
            player = await session.scalar(stmt)
            player.alive = False
            await session.commit()

    async def create_share(self, name: str, start_price: int) -> ShareModel:
        async with self.app.database.session() as session:
            share = ShareModel(
                name=name,
                start_price=start_price,
            )
            session.add(share)
            await session.commit()
        return share

    async def delete_share(self, share_id: int) -> None:
        stmt = select(ShareModel).where(ShareModel.id == share_id)
        async with self.app.database.session() as session:
            share = await session.scalar(stmt)
            await session.delete(share)
            await session.commit()

    async def update_start_share_price(self, share_id: int, price: int) -> None:
        stmt = select(ShareModel).where(ShareModel.id == share_id)
        async with self.app.database.session() as session:
            share = await session.scalar(stmt)
            share.start_price = price
            await session.commit()

    async def get_game_inventory(
        self, game_id: int
    ) -> list[GameInventoryModel]:
        async with self.app.database.session() as session:
            return list(
                await session.scalars(
                    select(GameInventoryModel).where(
                        GameInventoryModel.game_id == game_id
                    )
                )
            )

    async def add_share_to_inventory(
        self, share_id: int, game_id: int, share_price: int
    ) -> None:
        async with self.app.database.session() as session:
            game_inventory_item = GameInventoryModel(
                share_id=share_id,
                game_id=game_id,
                price=share_price,
            )
            session.add(game_inventory_item)
            await session.commit()

    async def change_item_price(
        self, game_id, share_id, share_price: int
    ) -> None:
        stmt = select(GameInventoryModel).where(
            and_(
                GameInventoryModel.share_id == share_id,
                GameInventoryModel.game_id == game_id,
            )
        )
        async with self.app.database.session() as session:
            game_inventory_item = await session.scalar(stmt)
            game_inventory_item.share_price = share_price
            await session.commit()

    async def get_player_inventory(
        self, player_id: int
    ) -> list[GameInventoryModel]:
        async with self.app.database.session() as session:
            return list(
                await session.scalars(
                    select(PlayerInventoryModel).where(
                        PlayerInventoryModel.share_owner == player_id
                    )
                )
            )

    async def add_share_to_player_inventory(
        self, share_id: int, player_id: int
    ) -> None:
        async with self.app.database.session() as session:
            player_inventory_item = PlayerInventoryModel(
                share_id=share_id,
                share_owner=player_id,
            )
            session.add(player_inventory_item)

            stmt = select(PlayerModel).where(PlayerModel.id == player_id)
            player = await session.scalar(stmt)

            stmt = select(GameInventoryModel).where(
                and_(
                    GameInventoryModel.game_id == player.game_id,
                    GameInventoryModel.share_id == share_id,
                )
            )
            game_inventory_price = (await session.scalar(stmt)).price

            player.balance -= game_inventory_price

            await session.commit()

    async def remove_share_from_player_inventory(
        self, share_id: int, player_id: int
    ) -> None:
        async with self.app.database.session() as session:
            stmt = select(PlayerInventoryModel).where(
                PlayerInventoryModel.share_id == share_id
            )
            player_inventory_item = await session.scalar(stmt)
            await session.delete(player_inventory_item)

            stmt = select(PlayerModel).where(PlayerModel.id == player_id)
            player = await session.scalar(stmt)

            stmt = select(GameInventoryModel).where(
                and_(
                    GameInventoryModel.game_id == player.game_id,
                    GameInventoryModel.share_id == share_id,
                )
            )
            game_inventory_price = (await session.scalar(stmt)).price

            player.balance += game_inventory_price

            await session.commit()
