import asyncio
import random
from asyncio import Queue

from app.game.models import PlayerModel
from app.store import Store
from app.telegram.admin_panel import AdminPanel
from app.telegram.keyboard import (
    game_keyboard_generator,
    info_keyboard_generator,
)
from app.telegram.messages import BotCommands, MessageType, TextMessage


class Bot:
    def __init__(self, store: Store):
        self.store = store
        self.player_balance: int | None = None
        self.turn_timer: int | None = None
        self.turn_counter: int | None = None
        self.minimal_shares_price: int | None = None
        self.maximum_shares_price: int | None = None
        self.settings = asyncio.create_task(self.setup_settings())
        self.queue = Queue()
        self.work = asyncio.create_task(self.worker())
        self.check_games = asyncio.create_task(self.check_unfinished_games())
        self.admin_panel = AdminPanel(store)

    async def setup_settings(self):
        while True:
            self.turn_timer = await self.store.settings.get_turn_timer()
            self.player_balance = await self.store.settings.get_player_balance()
            self.turn_counter = await self.store.settings.get_turn_counter()
            self.minimal_shares_price = (
                await self.store.settings.get_shares_minimal_price()
            )
            self.maximum_shares_price = (
                await self.store.settings.get_shares_maximum_price()
            )

    async def check_unfinished_games(self):
        games = await self.store.games.get_all_active_games()
        for game in games:
            task = asyncio.create_task(
                self.game_turn_controller(game_id=game.id)
            )

    async def worker(self):
        while True:
            task = await self.queue.get()
            self.queue.task_done()

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
        if not game or game.last_turn > 1:
            return
        players = await self.store.games.get_alive_players(game_id=game.id)
        if len(players) < 2:
            await self.store.games.finish_game(game_id=game.id)
            await self.queue.put(
                asyncio.create_task(
                    self.send_message_to_telegram(
                        message_type="info",
                        chat_id=chat_id,
                        text=TextMessage.players_count_not_enough.value,
                        keyboard=info_keyboard_generator(),
                    )
                )
            )
            return
        task = asyncio.create_task(self.game_turn_controller(game_id=game.id))

    async def create_player(self, user_id: int, game_id: int):
        player = await self.store.games.get_player_by_user_and_game_id(
            user_id=user_id, game_id=game_id
        )
        if not player:
            await self.store.games.create_player(
                user_id=user_id,
                game_id=game_id,
                balance=self.player_balance,
            )

    async def change_shares_price(self, game_id: int):
        shares = await self.store.games.get_game_inventory(game_id)
        for share in shares:
            new_price = random.randint(
                self.minimal_shares_price, self.maximum_shares_price
            )
            await self.store.games.change_item_price(
                game_id, share.share_id, new_price
            )

    async def finish_game(
        self,
        user_id: int | None = None,
        game_id: int | None = None,
        chat_id: int | None = None,
    ):
        if game_id is None:
            game = await self.store.games.get_game_by_chat_id(chat_id=chat_id)
            if not game:
                await self.queue.put(
                    asyncio.create_task(
                        self.send_message_to_telegram(
                            message_type="info",
                            chat_id=chat_id,
                            text="Нет активной игры",
                            keyboard=info_keyboard_generator(),
                        )
                    )
                )
                return
            game_id = game.id
        if user_id:
            user = await self.store.user.get_user_by_telegram_id(
                telegram_id=user_id
            )
            player = await self.store.games.get_player_by_user_and_game_id(
                user_id=user.id, game_id=game_id
            )
            # Game over protection
            if not player:
                return
        winner = await self.calculate_winner(game_id=game_id)
        user = await self.store.user.get_user_by_id(winner["winner"].user_id)
        message = f"Поздравляем победителя в нашей игре @{user.nickname}! Финальное состояние {winner['total_value']}."
        await self.store.games.finish_game(game_id=game_id)
        chat_id = (await self.store.games.get_game_by_id(game_id)).chat_id
        await self.queue.put(
            asyncio.create_task(
                self.send_message_to_telegram(
                    message_type="info",
                    chat_id=chat_id,
                    text=message,
                    keyboard=info_keyboard_generator(),
                )
            )
        )

    async def calculate_winner(
        self, game_id: int
    ) -> dict[str, [int, PlayerModel]]:
        players = await self.store.games.get_alive_players(game_id=game_id)
        maximum_value = 0
        winner = None
        for player in players:
            player_value = 0
            player_value += await self.store.games.get_player_balance(player.id)
            player_shares = await self.store.games.get_player_inventory(
                player.id
            )
            for share in player_shares:
                player_value += (
                    await self.store.games.get_game_inventory_item_by_share_id(
                        game_id=game_id, share_id=share.share_id
                    )
                ).price
            if player_value > maximum_value:
                maximum_value = player_value
                winner = player
        return {
            "winner": winner,
            "total_value": maximum_value,
        }

    async def start_bot(self, chat_id: int):
        game = await self.store.games.get_game_by_chat_id(chat_id=chat_id)
        if not game:
            await self.queue.put(
                asyncio.create_task(
                    self.send_message_to_telegram(
                        message_type="info",
                        chat_id=chat_id,
                        text=TextMessage.start_bot.value,
                        keyboard=info_keyboard_generator(),
                    )
                )
            )

    async def game_rules(self, chat_id: int):
        game = await self.store.games.get_game_by_chat_id(chat_id=chat_id)
        if not game:
            await self.queue.put(
                asyncio.create_task(
                    self.send_message_to_telegram(
                        message_type="info",
                        chat_id=chat_id,
                        text=TextMessage.game_rules.value,
                        keyboard=info_keyboard_generator(),
                    )
                )
            )

    async def bot_info(self, chat_id: int):
        game = await self.store.games.get_game_by_chat_id(chat_id=chat_id)
        if not game:
            await self.queue.put(
                asyncio.create_task(
                    self.send_message_to_telegram(
                        message_type="info",
                        chat_id=chat_id,
                        text=TextMessage.bot_info.value,
                        keyboard=info_keyboard_generator(),
                    )
                )
            )

    async def create_user(
        self, telegram_id: int, nickname: str, first_name: str
    ):
        user = await self.store.user.get_user_by_telegram_id(
            telegram_id=telegram_id
        )
        if not user:
            user = await self.store.user.create_user(
                telegram_id=telegram_id,
                nickname=nickname,
                first_name=first_name,
            )
        return user

    async def player_left_the_game(self, telegram_id: int, chat_id: int):
        game = await self.store.games.get_game_by_chat_id(chat_id=chat_id)
        if not game:
            return
        user = await self.store.user.get_user_by_telegram_id(
            telegram_id=telegram_id
        )
        player = await self.store.games.get_player_by_user_and_game_id(
            user_id=user.id, game_id=game.id
        )
        if player:
            await self.store.games.player_dead(player_id=player.id)

    async def game_turn_controller(self, game_id: int):
        while True:
            game = await self.store.games.get_game_by_id(game_id=game_id)
            players_count = len(
                await self.store.games.get_alive_players(game_id=game_id)
            )
            if not game.is_active:
                break
            if game.last_turn < self.turn_counter and players_count >= 2:
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
                await self.queue.put(
                    asyncio.create_task(
                        self.send_message_to_telegram(
                            message_type="new_game_message",
                            chat_id=(
                                await self.store.games.get_game_by_id(
                                    game_id=game_id
                                )
                            ).chat_id,
                            text=await self.make_game_message(
                                game_id=game_id,
                                game_inventory=formatted_game_inventory,
                            ),
                            keyboard=game_keyboard_generator(
                                formatted_game_inventory
                            ),
                        )
                    )
                )
                await asyncio.sleep(self.turn_timer)
                await self.change_shares_price(game_id=game_id)
                await self.store.games.increase_game_turn(game_id=game_id)
            else:
                await self.finish_game(game_id=game_id)
                break

    async def make_game_message(self, game_id: int, game_inventory):
        alive_players = await self.store.games.get_alive_players(
            game_id=game_id
        )
        players_info = await self.get_players_info(alive_players)
        return f"""
Представляю вашему вниманию состояние фондового рынка на текущий ход:
{'\n'.join([f'{item[0]}, {item[2]}' for item in game_inventory])}
Список игроков:
{'\n'.join([
f'{(await self.store.user.get_user_by_id(player.user_id)).first_name}' \
f'(@{(await self.store.user.get_user_by_id(player.user_id)).nickname})' \
f'Баланс: {player.balance} Инвентарь: {' '.join([
                        f'{x[0]}({x[1]})' for x in players_info[player.id]
                    ])}'
            for player in alive_players])}
                """

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
            game_id=game.id, share_id=share_id
        )
        if player.balance >= game_item.price:
            await self.store.games.add_share_to_player_inventory(
                player_id=player.id,
                share_id=share_id,
            )
        game_id = player.game_id
        await self.send_edit_game_message(
            game_id=game_id, chat_id=chat_id, message_id=message_id
        )

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
        await self.send_edit_game_message(
            game_id=game_id, chat_id=chat_id, message_id=message_id
        )

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
        await self.queue.put(
            asyncio.create_task(
                self.send_message_to_telegram(
                    message_type="edit_game_message",
                    chat_id=chat_id,
                    message_id=message_id,
                    text=await self.make_game_message(
                        game_id, formatted_game_inventory
                    ),
                    keyboard=game_keyboard_generator(formatted_game_inventory),
                )
            )
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

    async def parse_message(self, item):
        if item.get("message"):
            if item["message"]["chat"]["type"] == "private":
                await self.queue.put(
                    asyncio.create_task(
                        self.admin_panel.check_private_message(
                            message=item["message"]["text"],
                            telegram_id=item["message"]["chat"]["id"],
                        )
                    )
                )
                return
            if item["message"].get("new_chat_participant"):
                pass
            else:
                await self.check_message(
                    item["message"]["chat"]["id"],
                    item["message"]["text"],
                )

        elif item.get("poll"):
            await self.store.telegram_api.get_poll_results(item["poll"]["id"])
        elif item.get("poll_answer"):
            if item["poll_answer"]["option_ids"][0] == 0:
                if not item["poll_answer"]["user"].get("username"):
                    return
                user = await self.create_user(
                    telegram_id=item["poll_answer"]["user"]["id"],
                    nickname=item["poll_answer"]["user"]["username"],
                    first_name=item["poll_answer"]["user"]["first_name"],
                )
                game_id = (
                    await self.store.telegram_api.get_poll(
                        poll_id=item["poll_answer"]["poll_id"],
                    )
                ).game_id
                await self.create_player(
                    user_id=user.id,
                    game_id=game_id,
                )
        elif item.get("callback_query"):
            if item["callback_query"]["message"]["chat"]["type"] == "private":
                await self.queue.put(
                    asyncio.create_task(
                        self.admin_panel.check_private_message(
                            message=item,
                            telegram_id=item["callback_query"]["message"][
                                "chat"
                            ]["id"],
                        )
                    )
                )
            else:
                await self.check_message(
                    item["callback_query"]["message"]["chat"]["id"],
                    item["callback_query"]["data"],
                    item["callback_query"]["from"]["id"],
                    item["callback_query"]["message"]["message_id"],
                )
            await self.queue.put(
                asyncio.create_task(
                    self.send_message_to_telegram(
                        message_type="callback", id=item["callback_query"]["id"]
                    )
                )
            )

    async def send_message_to_telegram(
        self, message_type: str, *args, **kwargs
    ):
        if message_type == MessageType.callback.value:
            await self.store.telegram_api.send_answer_callback_query(
                kwargs["id"]
            )
        elif message_type == MessageType.new_game_message.value:
            await self.store.telegram_api.send_game_message(
                kwargs["chat_id"], kwargs["text"], kwargs["keyboard"]
            )
        elif message_type == MessageType.edit_game_message.value:
            await self.store.telegram_api.edit_game_message(
                kwargs["chat_id"],
                kwargs["message_id"],
                kwargs["text"],
                kwargs["keyboard"],
            )
        elif message_type == MessageType.info.value:
            await self.store.telegram_api.send_info_message_to_chat(
                kwargs["chat_id"], kwargs["text"], kwargs["keyboard"]
            )

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
            await self.finish_game(chat_id=chat_id, user_id=args[0])
        elif message == BotCommands.left_game.value:
            await self.player_left_the_game(
                chat_id=chat_id, telegram_id=args[0]
            )
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
