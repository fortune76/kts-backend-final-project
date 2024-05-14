from enum import Enum

from app.store import Store


class AdminCommands(Enum):
    update_turn_counter = "Изменить максимальное количество ходов"
    update_turn_timer = "Изменить время хода"
    update_player_balance = "Изменить стартовый баланс игроков"
    update_share_minimal_price = "Изменить минимальную стоимость акции"
    update_share_maximal_price = "Изменить максимальную стоимость акции"

class AdminPanel:
    def __init__(self, store: Store):
        self.store = store

    async def update_turn_counter(self, turn_counter: str):
        try:
            turn_counter = int(turn_counter)
            await self.store.settings.update_turn_counter(turn_counter=int(turn_counter))
            await self.store.telegram_api.send_admin_panel_message(message="Данные успешно изменены!")
        except ValueError:
            await self.store.telegram_api.send_admin_panel_message(message="Введенные данные не валидны!")

    async def update_turn_timer(self, turn_timer: str):
        try:
            turn_timer = int(turn_timer)
            await self.store.settings.update_turn_timer(turn_timer=int(turn_timer))
            await self.store.telegram_api.send_admin_panel_message(message="Данные успешно изменены!")
        except ValueError:
            await self.store.telegram_api.send_admin_panel_message(message="Введенные данные не валидны!")

    async def update_player_balance(self, player_balance: str):
        try:
            player_balance = int(player_balance)
            await self.store.settings.update_player_balance(player_balance=int(player_balance))
            await self.store.telegram_api.send_admin_panel_message(message="Данные успешно изменены!")
        except ValueError:
            await self.store.telegram_api.send_admin_panel_message(message="Введенные данные не валидны!")

    async def update_share_minimal_price(self, share_minimal_price: str):
        try:
            share_minimal_price = int(share_minimal_price)
            await self.store.settings.update_player_balance(share_minimal_price=int(share_minimal_price))
            await self.store.telegram_api.send_admin_panel_message(message="Данные успешно изменены!")
        except ValueError:
            await self.store.telegram_api.send_admin_panel_message(message="Введенные данные не валидны!")

    async def update_share_maximal_price(self, share_maximal_price: str):
        try:
            share_maximal_price = int(share_maximal_price)
            await self.store.settings.update_player_balance(share_maximal_price=int(share_maximal_price))
            await self.store.telegram_api.send_admin_panel_message(message="Данные успешно изменены!")
        except ValueError:
            await self.store.telegram_api.send_admin_panel_message(message="Введенные данные не валидны!")

    async def check_admin(self, telegram_id: int):
        if self.store.user.is_admin(telegram_id=telegram_id):
            return True
        return False

    async def undefined_message(self, admin: bool):
        if admin:
            await self.store.telegram_api.send_admin_panel_message(message="Список доступных команд:")
            return
        self.store.telegram_api.send_guest_message(message="Вас нет в списке администраторов. Доступ запрещен.")
    async def check_private_message(self, message: str, telegram_id: int):
        if self.check_admin(telegram_id):
            if message == AdminCommands.update_turn_counter.value:
                pass
            elif message == AdminCommands.update_turn_timer.value:
                pass
            elif message == AdminCommands.update_player_balance.value:
                pass
            elif message == AdminCommands.update_share_minimal_price.value:
                pass
            elif message == AdminCommands.update_share_maximal_price.value:
                pass
            else:
                await self.undefined_message(admin=True)
        else:
            await self.undefined_message(admin=False)