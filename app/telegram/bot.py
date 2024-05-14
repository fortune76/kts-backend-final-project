import asyncio
import random

from app.game.models import PlayerModel
from app.store import Store

from app.telegram.messages import BotCommands, TextMessage


class Bot:
    def __init__(self, store: Store):
        self.store = store
        self.player_balance = 1000
        self.turn_time = 30
        self.max_turn = 5

    # TODO: добавить проверку при старте,
    #  если есть активные игры перезапускать таску.

    async def create_game(self, chat_id: int):
        game_exists = await self.store.games.get_game_by_chat_id(
            chat_id=chat_id
        )
        if game_exists and game_exists.is_active:
            return
        game = await self.store.games.create_game(chat_id)
        await self.store.games.increase_game_turn(game_id=game.id)
        await self.store.telegram_api.send_start_poll(
            chat_id=chat_id, game_id=game.id
        )
        shares = await self.store.games.get_shares()
        for share in shares:
            await self.store.games.add_share_to_inventory(
                share_id=share.id,
                game_id=game.id,
                share_price=share.start_price,
            )

    async def start_game(self, chat_id: int):
        game = await self.store.games.get_game_by_chat_id(chat_id=chat_id)
        if not game:
            return
        players = await self.store.games.get_alive_players(game_id=game.id)
        if len(players) < 2:
            await self.store.games.finish_game(game_id=game.id)
            await self.store.telegram_api.send_message_with_keyboard(
                chat_id=chat_id,
                text=TextMessage.players_count_not_enough.value,
            )
            return
        if not game or game.last_turn > 1:
            return
        task = asyncio.create_task(self.game_turn_controller(game_id=game.id))

    async def create_player(self, user_id: int, game_id: int):
        await self.store.games.create_player(
            user_id=user_id,
            game_id=game_id,
            balance=self.player_balance,
        )

    async def change_shares_price(self, game_id: int):
        shares = await self.store.games.get_game_inventory(game_id)
        for share in shares:
            new_price = random.randint(1, 400)
            await self.store.games.change_item_price(
                game_id, share.share_id, new_price
            )

    # async def get_player_info(self, player_id: int):
    #     player = await self.store.games.get_player_by_id(player_id=player_id)
    #     inventory = await self.store.games.get_player_inventory(
    #         player_id=player.id
    #     )

    async def finish_game(
        self, game_id: int | None = None, chat_id: int | None = None
    ):
        if game_id is None:
            game = await self.store.games.get_game_by_chat_id(chat_id=chat_id)
            if not game:
                return
            await self.store.games.finish_game(game_id=game.id)
        else:
            await self.store.games.finish_game(game_id=game_id)
        # # TODO: такого метода нет, создать
        # winner = await self.store.games.get_winner(game_id=game_id)

    async def start_bot(self, chat_id: int):
        await self.store.telegram_api.send_message_with_keyboard(
            chat_id=chat_id,
            text=TextMessage.start_bot.value,
        )

    async def game_rules(self, chat_id: int):
        await self.store.telegram_api.send_message_with_keyboard(
            chat_id=chat_id,
            text=TextMessage.game_rules.value,
        )

    async def bot_info(self, chat_id: int):
        await self.store.telegram_api.send_message_with_keyboard(
            chat_id=chat_id,
            text=TextMessage.bot_info.value,
        )

    async def create_user(
        self, telegram_id: int, nickname: str, first_name: str
    ):
        user = await self.store.user.get_user_by_telegram_id(
            telegram_id=telegram_id
        )
        if user:
            return
        user = await self.store.user.create_user(
            telegram_id=telegram_id,
            nickname=nickname,
            first_name=first_name,
        )

    async def game_turn_controller(self, game_id: int):
        while True:
            game = await self.store.games.get_game_by_id(game_id=game_id)
            if not game.is_active:
                break
            if game.last_turn < 6:
                game_inventory = await self.store.games.get_game_inventory(
                    game_id=game_id
                )
                formatted_game_inventory = [
                    [
                        (
                            await self.store.games.get_share_by_id(
                                item.share_id
                            )
                        ).name,
                        item.share_id,
                        item.price,
                    ]
                    for item in game_inventory
                ]
                alive_players = await self.store.games.get_alive_players(
                    game_id=game_id
                )
                players_info = await self.get_players_info(alive_players)
                await self.store.telegram_api.send_game_message(
                    chat_id=(
                        await self.store.games.get_game_by_id(game_id=game_id)
                    ).chat_id,
                    game_inventory=formatted_game_inventory,
                    text=f"""
Представляю вашему вниманию состояние фондового рынка на текущий ход:
{'\n'.join([f'{item[0]}, {item[2]}' for item in formatted_game_inventory])}
Список игроков:
{'\n'.join([
f'{(await self.store.user.get_user_by_id(player.user_id)).first_name} \
Баланс: {player.balance} Инвентарь: {[
                        f"{x[0]}({x[1]})"for x in players_info[player.id]
                    ]}'
            for player in alive_players])}
                """,
                )
                await asyncio.sleep(10)
                await self.change_shares_price(game_id=game_id)
                await self.store.games.increase_game_turn(game_id=game_id)
            else:
                await self.finish_game(game_id=game_id)
                break

    async def player_buys(
        self, user_id: int, chat_id: int, share_id: int, message_id: int
    ):
        user = await self.store.user.get_user_by_telegram_id(
            telegram_id=user_id
        )
        game = await self.store.games.get_game_by_chat_id(chat_id=chat_id)
        if not all([user, game]):
            return
        player = await self.store.games.get_player_by_user_and_game_id(
            user_id=user.id, game_id=game.id
        )
        game_item = await self.store.games.get_game_inventory_item_by_share_id(
            share_id=share_id
        )
        print(player.balance, game_item.price)
        if player.balance >= game_item.price:
            await self.store.games.add_share_to_player_inventory(
                player_id=player.id,
                share_id=share_id,
            )
        game_id = player.game_id
        await self.send_edit_game_message(game_id, chat_id, message_id)

    async def player_sells(
        self, user_id: int, chat_id: int, share_id: int, message_id: int
    ):
        user = await self.store.user.get_user_by_telegram_id(
            telegram_id=user_id
        )
        game = await self.store.games.get_game_by_chat_id(chat_id=chat_id)
        if not all([user, game]):
            return
        player = await self.store.games.get_player_by_user_and_game_id(
            user_id=user.id, game_id=game.id
        )
        player_shares = await self.store.games.get_player_shares(
            player_id=player.id
        )
        if not list(filter(lambda x: x.id == share_id, player_shares)):
            return
        await self.store.games.remove_share_from_player_inventory(
            player_id=player.id,
            share_id=share_id,
        )
        game_id = player.game_id
        await self.send_edit_game_message(game_id, chat_id, message_id)

    async def send_edit_game_message(
        self, game_id: int, chat_id: int, message_id: int
    ):
        game_inventory = await self.store.games.get_game_inventory(
            game_id=game_id
        )
        formatted_game_inventory = [
            [
                (await self.store.games.get_share_by_id(item.share_id)).name,
                item.share_id,
                item.price,
            ]
            for item in game_inventory
        ]
        alive_players = await self.store.games.get_alive_players(
            game_id=game_id
        )
        players_info = await self.get_players_info(alive_players)
        await self.store.telegram_api.edit_game_message(
            chat_id=chat_id,
            message_id=message_id,
            game_inventory=formatted_game_inventory,
            text=f"""
Представляю вашему вниманию состояние фондового рынка на текущий ход:
{'\n'.join([f'{item[0]}, {item[2]}' for item in formatted_game_inventory])}
Список игроков:
{'\n'.join([
f'{(await self.store.user.get_user_by_id(player.user_id)).first_name} \
Баланс: {player.balance} Инвентарь: {[
                        f"{x[0]}({x[1]})"for x in players_info[player.id]
                    ]}'
            for player in alive_players])}
                """,
        )

    async def get_players_info(
        self, players: list[PlayerModel]
    ) -> dict[int, list[list]]:
        result = {}
        for player in players:
            player_shares = [
                [
                    item.name,
                    await self.store.games.get_count_of_items(
                        item.id, player.id
                    ),
                ]
                for item in (
                    await self.store.games.get_player_shares(
                        player_id=player.id
                    )
                )
            ]
            result[player.id] = player_shares
        return result

    async def check_message(self, chat_id: int, message: str, *args):
        complex_callback_message = message.split()
        if message == BotCommands.start_bot.value:
            await self.start_bot(chat_id=chat_id)
        elif message == BotCommands.game_rules.value:
            await self.game_rules(chat_id=chat_id)
        elif message == BotCommands.bot_info.value:
            await self.bot_info(chat_id=chat_id)
        elif message == BotCommands.create_game.value:
            await self.create_game(chat_id=chat_id)
        elif message == BotCommands.start_game.value:
            await self.start_game(chat_id=chat_id)
        elif message == BotCommands.finish_game.value:
            await self.finish_game(chat_id=chat_id)
        elif complex_callback_message[0] == "купить":
            await self.player_buys(
                user_id=args[0],
                chat_id=chat_id,
                share_id=int(complex_callback_message[1]),
                message_id=args[1],
            )
        elif complex_callback_message[0] == "продать":
            await self.player_sells(
                user_id=args[0],
                chat_id=chat_id,
                share_id=int(complex_callback_message[1]),
                message_id=args[1],
            )
        else:
            pass
