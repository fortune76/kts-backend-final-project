from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.game.models import (
    GameModel,
    PlayerModel,
    ShareModel,
)
from app.store import Store
from tests.utils import (
    game_inventory_to_dict,
    game_to_dict,
    player_inventory_to_dict,
    player_to_dict,
    share_to_dict,
)


class TestGameAccessor:
    async def test_table_exists(self, inspect_list_tables: list[str]):
        assert "games" in inspect_list_tables
        assert "players" in inspect_list_tables
        assert "shares" in inspect_list_tables
        assert "game_inventory" in inspect_list_tables
        assert "player_inventory" in inspect_list_tables

    async def test_create_game(
        self,
        db_sessionmaker: async_sessionmaker[AsyncSession],
        store: Store,
        freeze_t,
    ):
        game = await store.games.create_game(chat_id=111)
        assert isinstance(game, GameModel)

        async with db_sessionmaker() as session:
            db_game = await session.scalar(
                select(GameModel).where(GameModel.chat_id == 111)
            )

        assert game_to_dict(db_game) == {
            "id": 1,
            "chat_id": 111,
            "started_at": freeze_t,
            "finish_at": None,
            "is_active": True,
            "last_turn": 0,
        }

    async def test_get_game_by_id(
        self,
        db_sessionmaker: async_sessionmaker[AsyncSession],
        game_1,
        store: Store,
    ):
        game = await store.games.get_game_by_id(game_1.id)
        assert isinstance(game, GameModel)
        assert game.id == game_1.id

    async def test_increase_game_turn(
        self,
        db_sessionmaker: async_sessionmaker[AsyncSession],
        game_1,
        store: Store,
    ):
        await store.games.increase_game_turn(game_1.id)

        async with db_sessionmaker() as session:
            game_after_increase = await session.scalar(
                select(GameModel).where(GameModel.id == game_1.id)
            )

        assert game_after_increase.last_turn != game_1.last_turn
        assert game_after_increase.last_turn == 1

    async def test_finish_game(
        self,
        db_sessionmaker: async_sessionmaker[AsyncSession],
        game_1,
        store: Store,
        freeze_t,
    ):
        await store.games.finish_game(game_1.id)
        async with db_sessionmaker() as session:
            game_after_finish = await session.scalar(
                select(GameModel).where(GameModel.id == game_1.id)
            )

        assert game_after_finish.finish_at == freeze_t

    async def test_create_player(
        self,
        db_sessionmaker: async_sessionmaker[AsyncSession],
        store: Store,
        user_1,
        game_1,
    ):
        player = await store.games.create_player(
            user_id=user_1.id,
            balance=500,
            game_id=game_1.id,
        )
        assert isinstance(player, PlayerModel)
        async with db_sessionmaker() as session:
            db_player = await session.scalar(
                select(PlayerModel).where(PlayerModel.user_id == user_1.id)
            )

        assert player_to_dict(db_player) == {
            "id": 1,
            "balance": 500,
            "game_id": game_1.id,
            "user_id": user_1.id,
            "alive": True,
        }

    async def test_get_player_balance(
        self,
        db_sessionmaker: async_sessionmaker[AsyncSession],
        store: Store,
        player,
    ):
        balance = await store.games.get_player_balance(player.id)
        assert balance == 1000

    async def test_get_player_by_id(
        self,
        db_sessionmaker: async_sessionmaker[AsyncSession],
        store: Store,
        player,
    ):
        player = await store.games.get_player_by_id(player.id)
        assert isinstance(player, PlayerModel)
        assert player.id == 1

    async def test_update_player_balance(
        self,
        db_sessionmaker: async_sessionmaker[AsyncSession],
        store: Store,
        player,
    ):
        await store.games.update_player_balance(player.id, 500, "increase")
        async with db_sessionmaker() as session:
            db_player = await session.scalar(
                select(PlayerModel).where(PlayerModel.id == player.id)
            )
        assert db_player.balance == 1500

        await store.games.update_player_balance(player.id, 500, "decrease")
        async with db_sessionmaker() as session:
            db_player = await session.scalar(
                select(PlayerModel).where(PlayerModel.id == player.id)
            )
        assert db_player.balance == 1000

        await store.games.update_player_balance(player.id, 5000, "decrease")
        async with db_sessionmaker() as session:
            db_player = await session.scalar(
                select(PlayerModel).where(PlayerModel.id == player.id)
            )
        assert db_player.balance == 0

    async def test_player_dead(
        self,
        db_sessionmaker: async_sessionmaker[AsyncSession],
        store: Store,
        player,
    ):
        db_player = await store.games.get_player_by_id(player.id)
        assert db_player.alive is True

        await store.games.player_dead(player.id)
        async with db_sessionmaker() as session:
            db_player = await session.scalar(
                select(PlayerModel).where(PlayerModel.id == player.id)
            )

        assert db_player.alive is False

    async def test_create_share(
        self,
        db_sessionmaker: async_sessionmaker[AsyncSession],
        store: Store,
    ):
        share = await store.games.create_share(
            name="Lukoil",
            start_price=250,
        )
        assert isinstance(share, ShareModel)
        async with db_sessionmaker() as session:
            db_share = await session.scalar(
                select(ShareModel).where(ShareModel.id == 1)
            )

        assert share_to_dict(db_share) == {
            "id": 1,
            "name": "Lukoil",
            "start_price": 250,
        }

    async def test_delete_share(
        self,
        db_sessionmaker: async_sessionmaker[AsyncSession],
        store: Store,
        share_1,
    ):
        async with db_sessionmaker() as session:
            db_share = await session.scalar(
                select(ShareModel).where(ShareModel.id == share_1.id)
            )

        assert isinstance(db_share, ShareModel)
        await store.games.delete_share(share_1.id)
        async with db_sessionmaker() as session:
            db_share = await session.scalar(
                select(ShareModel).where(ShareModel.id == share_1.id)
            )

        assert db_share is None

    async def test_update_share_price(
        self,
        db_sessionmaker: async_sessionmaker[AsyncSession],
        store: Store,
        share_1,
    ):
        async with db_sessionmaker() as session:
            db_share = await session.scalar(
                select(ShareModel).where(ShareModel.id == share_1.id)
            )

        assert db_share.start_price == 100
        await store.games.update_start_share_price(share_1.id, 800)
        async with db_sessionmaker() as session:
            db_share = await session.scalar(
                select(ShareModel).where(ShareModel.id == share_1.id)
            )

        assert db_share.start_price == 800

    async def test_get_game_inventory(
        self,
        db_sessionmaker: async_sessionmaker[AsyncSession],
        store: Store,
        game_1,
        game_inventory_1,
        game_inventory_2,
    ):
        game_inventory = await store.games.get_game_inventory(game_1.id)
        assert game_inventory_to_dict(game_inventory) == [
            {
                "share_id": game_inventory_1.share_id,
                "game_id": game_1.id,
                "price": game_inventory_1.price,
            },
            {
                "share_id": game_inventory_2.share_id,
                "game_id": game_1.id,
                "price": game_inventory_2.price,
            },
        ]

    async def test_add_item_to_game_inventory(
        self,
        db_sessionmaker: async_sessionmaker[AsyncSession],
        store: Store,
        game_1,
        game_inventory_1,
        game_inventory_2,
        share_3,
    ):
        game_inventory = await store.games.get_game_inventory(game_1.id)
        len_before_add = len(game_inventory)
        await store.games.add_share_to_inventory(share_3.id, game_1.id, 600)
        game_inventory = await store.games.get_game_inventory(game_1.id)

        assert len(game_inventory) > len_before_add

    async def test_get_player_inventory(
        self,
        db_sessionmaker: async_sessionmaker[AsyncSession],
        store: Store,
        player,
        player_inventory_1,
        game_inventory_1,
    ):
        player_inventory = await store.games.get_player_inventory(player.id)
        assert player_inventory is not None
        assert player_inventory_to_dict(player_inventory) == [
            {
                "id": 1,
                "share_id": game_inventory_1.share_id,
                "share_owner": player.id,
            }
        ]

    async def test_add_share_to_player_inventory(
        self,
        db_sessionmaker: async_sessionmaker[AsyncSession],
        store: Store,
        player,
        player_inventory_1,
        game_inventory_2,
    ):
        player_inventory = await store.games.get_player_inventory(player.id)
        player_inventory_size = len(player_inventory)
        player_balance = await store.games.get_player_balance(player.id)

        assert player_balance == player.balance
        assert player_inventory is not None

        await store.games.add_share_to_player_inventory(
            game_inventory_2.share_id, player.id
        )
        player_inventory = await store.games.get_player_inventory(player.id)
        player_balance = await store.games.get_player_balance(player.id)

        assert player_balance < player.balance
        assert player_inventory_size < len(player_inventory)

    async def test_remove_share_from_player_inventory(
        self,
        db_sessionmaker: async_sessionmaker[AsyncSession],
        store: Store,
        player,
        player_inventory_1,
        game_inventory_1,
    ):
        player_inventory = await store.games.get_player_inventory(player.id)
        player_balance = await store.games.get_player_balance(player.id)
        assert player_inventory is not None
        assert player_balance == player.balance

        await store.games.remove_share_from_player_inventory(
            game_inventory_1.share_id, player.id
        )
        player_inventory = await store.games.get_player_inventory(player.id)
        player_balance = await store.games.get_player_balance(player.id)
        assert player_balance > player.balance
        assert player_inventory == []
