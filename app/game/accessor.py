import datetime

from sqlalchemy import and_, delete, func, select, update

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

    async def get_all_active_games(self) -> list[GameModel]:
        stmt = select(GameModel).where(GameModel.is_active == True)
        async with self.app.database.session() as session:
            return list(await session.scalars(stmt))

    async def get_game_by_id(self, game_id: int) -> GameModel:
        stmt = select(GameModel).where(GameModel.id == game_id)
        async with self.app.database.session() as session:
            return await session.scalar(stmt)

    async def get_game_by_chat_id(self, chat_id: int) -> GameModel:
        stmt = select(GameModel).where(
            and_(GameModel.chat_id == chat_id, GameModel.is_active == True)
        )
        async with self.app.database.session() as session:
            return await session.scalar(stmt)

    async def increase_game_turn(self, game_id: int) -> None:
        stmt = (
            update(GameModel)
            .where(GameModel.id == game_id)
            .values(last_turn=GameModel.last_turn + 1)
        )
        async with self.app.database.session() as session:
            await session.execute(stmt)
            await session.commit()

    async def finish_game(self, game_id: int) -> None:
        datetime_now = datetime.datetime.now()
        stmt = (
            update(GameModel)
            .where(GameModel.id == game_id)
            .values(finish_at=datetime_now, is_active=False)
        )
        async with self.app.database.session() as session:
            await session.execute(stmt)
            await session.commit()

    async def get_all_finished_games(self) -> list[GameModel]:
        stmt = select(GameModel).where(GameModel.is_active == False)
        async with self.app.database.session() as session:
            return list(await session.scalars(stmt))

    async def get_last_chat_game(self, chat_id: int) -> GameModel:
        stmt = select(GameModel).where(
            GameModel.chat_id == chat_id,
            GameModel.is_active == False).order_by(GameModel.finish_at).limit(1)
        async with self.app.database.session() as session:
            return await session.scalar(stmt)

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

    async def get_player_by_user_and_game_id(
        self, user_id: int, game_id: int
    ) -> PlayerModel | None:
        stmt = select(PlayerModel).where(
            and_(PlayerModel.user_id == user_id, PlayerModel.game_id == game_id)
        )
        async with self.app.database.session() as session:
            player = await session.scalar(stmt)
            return player if player else None

    async def get_player_balance(self, player_id: int) -> int:
        stmt = select(PlayerModel.balance).where(PlayerModel.id == player_id)
        async with self.app.database.session() as session:
            return await session.scalar(stmt)

    async def get_alive_players(self, game_id: int) -> list[PlayerModel]:
        stmt = (
            select(PlayerModel)
            .where(
                and_(PlayerModel.game_id == game_id, PlayerModel.alive == True)
            )
            .order_by(PlayerModel.id)
        )
        async with self.app.database.session() as session:
            return list(await session.scalars(stmt))

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
        stmt = (
            update(PlayerModel)
            .where(PlayerModel.id == player_id)
            .values(alive=False)
        )
        async with self.app.database.session() as session:
            await session.execute(stmt)
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

    async def get_shares(self) -> list[ShareModel]:
        async with self.app.database.session() as session:
            return list(
                await session.scalars(
                    select(ShareModel).order_by(ShareModel.id)
                )
            )

    async def get_share_by_id(self, share_id: int) -> ShareModel:
        async with self.app.database.session() as session:
            return await session.scalar(
                select(ShareModel).where(ShareModel.id == share_id)
            )

    async def get_share_by_name(self, share_name: str) -> ShareModel:
        async with self.app.database.session() as session:
            return await session.scalar(
                select(ShareModel).where(ShareModel.name == share_name)
            )

    async def delete_share(self, share_id: int) -> None:
        stmt = delete(ShareModel).where(ShareModel.id == share_id)
        async with self.app.database.session() as session:
            await session.execute(stmt)
            await session.commit()

    async def update_start_share_price(self, share_id: int, price: int) -> None:
        stmt = (
            update(ShareModel)
            .where(ShareModel.id == share_id)
            .values(start_price=price)
        )
        async with self.app.database.session() as session:
            await session.execute(stmt)
            await session.commit()

    async def get_game_inventory(
        self, game_id: int
    ) -> list[GameInventoryModel]:
        async with self.app.database.session() as session:
            return list(
                await session.scalars(
                    select(GameInventoryModel)
                    .where(GameInventoryModel.game_id == game_id)
                    .order_by(GameInventoryModel.id)
                )
            )

    async def get_game_inventory_item_by_share_id(
        self, share_id: int, game_id: int
    ) -> GameInventoryModel:
        stmt = select(GameInventoryModel).where(
            GameInventoryModel.share_id == share_id,
            GameInventoryModel.game_id == game_id,
        )
        async with self.app.database.session() as session:
            return await session.scalar(stmt)

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
        stmt = (
            update(GameInventoryModel)
            .where(
                and_(
                    GameInventoryModel.share_id == share_id,
                    GameInventoryModel.game_id == game_id,
                )
            )
            .values(price=share_price)
        )
        async with self.app.database.session() as session:
            await session.execute(stmt)
            await session.commit()

    async def get_player_inventory(
        self, player_id: int
    ) -> list[PlayerInventoryModel]:
        async with self.app.database.session() as session:
            return list(
                await session.scalars(
                    select(PlayerInventoryModel)
                    .where(PlayerInventoryModel.share_owner == player_id)
                    .order_by(PlayerInventoryModel.id)
                )
            )

    async def get_count_of_items(self, share_id: int, player_id: int) -> int:
        stmt = (
            select(func.count(PlayerInventoryModel.share_id))
            .select_from(PlayerInventoryModel)
            .where(
                and_(
                    PlayerInventoryModel.share_id == share_id,
                    PlayerInventoryModel.share_owner == player_id,
                )
            )
        )
        async with self.app.database.session() as session:
            return await session.scalar(stmt)

    async def get_player_shares(self, player_id: int) -> list[str]:
        stmt = (
            select(ShareModel)
            .distinct()
            .join(
                PlayerInventoryModel,
                ShareModel.id == PlayerInventoryModel.share_id,
            )
            .where(PlayerInventoryModel.share_owner == player_id)
        ).order_by(ShareModel.id)
        async with self.app.database.session() as session:
            return list(await session.scalars(stmt))

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
            item_stmt = select(PlayerInventoryModel.id).where(
                PlayerInventoryModel.share_id == share_id,
                PlayerInventoryModel.share_owner == player_id,
            )
            id_ = await session.scalar(item_stmt)
            stmt = delete(PlayerInventoryModel).where(
                PlayerInventoryModel.share_id == share_id,
                PlayerInventoryModel.id == id_,
            )
            await session.execute(stmt)

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
