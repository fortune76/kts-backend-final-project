from enum import Enum


class BotCommands(Enum):
    start_bot = "Привет биржа"
    create_game = "Кто будет играть?"
    start_game = "Начать игру"
    finish_game = "Завершить игру"
    game_rules = "Правила игры"
    bot_info = "О боте"
    left_game = "Покинуть игру"


class TextMessage(Enum):
    game_rules = """Правила игры: 
Игра является простой версией биржы фондового рынка. \
Игроки покупают и продают активы, цена которых постоянно меняется.
 
Игра длится 5 ходов. Время одного хода - 30 секунд. \
В течение этого времени игроки могут продать и купить активы.
 
Цена на активы меняется случайным образом каждый ход. \
Т.е. купив дорогие активы сейчас, на следующий ход вы можете 
остаться ни с чем. 

Игра заканчивается, когда в игре осталось меньше двух игроков \
или закончились ходы. Побеждает игрок чей баланс, \
включая стоимость активов в портфеле, наибольший.

Счастливых вам биржевых игр и пусть удача всегда будет с вами!
        """
    bot_info = """Игровой бот биржа был разработан в \
качестве выпускного проекта курса от компании KTS.
Разработчик - @smdoff, ментор - @ipakeev.
Бот разработан на языке python, без использования специальных библиотек.
        """
    start_bot = f"""Привет, я игровой бот Биржа! 
Для начала игры напишите в чат {BotCommands.create_game.value}
После сбора игроков напишите в чат {BotCommands.start_bot.value}
Для досрочного завершения игры напишите в чат {BotCommands.finish_game.value}
Не знаете правила игры? Напишите в чат {BotCommands.game_rules.value}
Если вы хотите узнать больше обо мне напишите {BotCommands.bot_info.value}.

Внимание! Для игры нужно обязательно иметь username в telegram. \
Бот не будет играть с пользователями без username.
        """
    players_count_not_enough = """К сожалению игра не может быть начата. \
Недостаточное количество игроков."""


class MessageType(Enum):
    callback = "callback"
    new_game_message = "new_game_message"
    edit_game_message = "edit_game_message"
    info = "info"


class AdminCommands(Enum):
    update_turn_counter = "turn_counter"
    update_turn_timer = "turn_timer"
    update_player_balance = "player_balance"
    update_share_minimal_price = "share_minimal_price"
    update_share_maximal_price = "share_maximum_price"
