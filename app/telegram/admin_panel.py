from app.store import Store
from app.telegram.keyboard import (
    get_admin_keyboard,
    get_main_admin_keyboard,
)
from app.telegram.messages import AdminCommands


class AdminPanel:
    def __init__(self, store: Store):
        self.store = store

    async def update_turn_counter(self, turn_counter: str, chat_id: int):
        games = await self.store.games.get_all_active_games()
        if not games:
            await self.store.settings.update_turn_counter(
                turn_counter=int(turn_counter)
            )
            await self.main_menu(chat_id=chat_id)
        else:
            await self.store.telegram_api.send_basic_message(
                chat_id=chat_id,
                text="Есть активная игра, невозможно изменить настройки.",
            )

    async def update_turn_timer(self, turn_timer: str, chat_id: int):
        games = await self.store.games.get_all_active_games()
        if not games:
            await self.store.settings.update_turn_timer(
                turn_timer=int(turn_timer)
            )
            await self.main_menu(chat_id=chat_id)
        else:
            await self.store.telegram_api.send_basic_message(
                chat_id=chat_id,
                text="Есть активная игра, невозможно изменить настройки.",
            )

    async def update_player_balance(self, player_balance: str, chat_id: int):
        games = await self.store.games.get_all_active_games()
        if not games:
            await self.store.settings.update_player_balance(
                player_balance=int(player_balance)
            )
            await self.main_menu(chat_id=chat_id)
        else:
            await self.store.telegram_api.send_basic_message(
                chat_id=chat_id,
                text="Есть активная игра, невозможно изменить настройки.",
            )

    async def update_share_minimal_price(
        self, share_minimal_price: str, chat_id: int
    ):
        games = await self.store.games.get_all_active_games()
        if not games:
            await self.store.settings.update_shares_minimal_price(
                shares_minimal_price=int(share_minimal_price)
            )
            await self.main_menu(chat_id=chat_id)
        else:
            await self.store.telegram_api.send_basic_message(
                chat_id=chat_id,
                text="Есть активная игра, невозможно изменить настройки.",
            )

    async def update_share_maximum_price(
        self, share_maximum_price: str, chat_id: int
    ):
        games = await self.store.games.get_all_active_games()
        if not games:
            await self.store.settings.update_shares_maximum_price(
                shares_maximum_price=int(share_maximum_price)
            )
            await self.main_menu(chat_id=chat_id)
        else:
            await self.store.telegram_api.send_basic_message(
                chat_id=chat_id,
                text="Есть активная игра, невозможно изменить настройки.",
            )

    async def create_share(
        self, chat_id: int, share_name: str, share_start_price: str
    ):
        if int(share_start_price) > 0:
            share = await self.store.games.create_share(
                share_name, int(share_start_price)
            )
            await self.store.telegram_api.send_basic_message(
                chat_id=chat_id, text="Акция успешно добавлена."
            )
            await self.main_menu(chat_id=chat_id)
        else:
            await self.store.telegram_api.send_basic_message(
                chat_id=chat_id,
                text="Некорректная цена акции. Попробуйте снова.",
            )
            await self.main_menu(chat_id=chat_id)

    async def delete_share(self, chat_id: int, share_name: str):
        share = await self.store.games.get_share_by_name(share_name)
        if not share:
            await self.store.telegram_api.send_basic_message(
                chat_id=chat_id, text="Акции с таким названием не существует."
            )
            await self.main_menu(chat_id=chat_id)
        else:
            await self.store.games.delete_share(share.id)
            await self.store.telegram_api.send_basic_message(
                chat_id=chat_id, text="Акции успешно удалена."
            )
            await self.main_menu(chat_id=chat_id)

    async def main_menu(self, chat_id: int):
        turn_timer = await self.store.settings.get_turn_timer()
        turn_counter = await self.store.settings.get_turn_counter()
        player_balance = await self.store.settings.get_player_balance()
        share_minimal_price = (
            await self.store.settings.get_shares_minimal_price()
        )
        share_maximum_price = (
            await self.store.settings.get_shares_maximum_price()
        )
        shares = await self.store.games.get_shares()
        message = f"""Текущие настройки:
Таймер хода: {turn_timer} секунд
Количество ходов: {turn_counter} {'хода' if turn_counter < 5 else 'ходов'}
Стартовый баланс игрока: {player_balance} монет
Минимальная цена акции: {share_minimal_price} \
{'монет' if share_minimal_price == 0 else 'монета'}
Максимальная цена акции: {share_maximum_price} монет

Акции:
{'\n'.join(
            ['. Стартовая цена: '.join(
                [item.name, str(item.start_price)]
            ) for item in shares]
        )}

Для добавления новой акции напишите в чат: Добавить Имя акции стоимость.
Для удаления акции напишите в чат: Удалить Имя акции.
        """
        await self.store.telegram_api.send_admin_panel_message(
            chat_id=chat_id,
            text=message,
            keyboard=get_main_admin_keyboard(),
        )

    async def undefined_message(self, chat_id: int):
        await self.store.telegram_api.send_basic_message(
            chat_id=chat_id,
            text="Вас нет в списке администраторов. Доступ запрещен.",
        )

    async def change_settings(self, chat_id: int, setting_type: str):
        await self.store.telegram_api.send_admin_panel_message(
            chat_id=chat_id,
            text="Выберите новое значение с помощью кнопок",
            keyboard=get_admin_keyboard(setting_type=setting_type),
        )

    async def check_private_message(self, message, telegram_id: int):
        is_admin = await self.store.user.is_admin(telegram_id=telegram_id)
        if is_admin:
            if isinstance(message, str):
                if message == "Настройки":
                    await self.main_menu(chat_id=telegram_id)
                elif message.split()[0] == "Добавить":
                    await self.create_share(
                        telegram_id, message.split()[1], message.split()[2]
                    )
                elif message.split()[0] == "Удалить":
                    await self.delete_share(telegram_id, message.split()[1])

            if not isinstance(message, str) and message.get("callback_query"):
                admin_commands = {item.value for item in AdminCommands}
                if message["callback_query"]["data"] in admin_commands:
                    await self.change_settings(
                        chat_id=telegram_id,
                        setting_type=message["callback_query"]["data"],
                    )
                    return
                message_with_new_value = message["callback_query"][
                    "data"
                ].split()
                if message_with_new_value[0] == "turn_timer":
                    await self.update_turn_timer(
                        message_with_new_value[1], chat_id=telegram_id
                    )
                elif message_with_new_value[0] == "turn_counter":
                    await self.update_turn_counter(
                        message_with_new_value[1], chat_id=telegram_id
                    )
                elif message_with_new_value[0] == "player_balance":
                    await self.update_player_balance(
                        message_with_new_value[1], chat_id=telegram_id
                    )
                elif message_with_new_value[0] == "share_minimal_price":
                    await self.update_share_minimal_price(
                        message_with_new_value[1], chat_id=telegram_id
                    )
                elif message_with_new_value[0] == "share_maximum_price":
                    await self.update_share_maximum_price(
                        message_with_new_value[1], chat_id=telegram_id
                    )

        else:
            await self.undefined_message(chat_id=telegram_id)
