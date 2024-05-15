import json


async def game_keyboard_generator(data: list):
    shares_buttons = [
                [
                    {
                        "text": f"{item[0]} купить",
                        "callback_data": f"купить {item[1]}",
                    },
                    {
                        "text": f"{item[0]} продать",
                        "callback_data": f"продать {item[1]}",
                    },
                ]
                for item in data
            ]
    option_buttons = [
        [
            {
                "text": "Покинуть игру",
                "callback_data": "Покинуть игру",
            },
        ],
        [
            {
                "text": "Завершить игру",
                "callback_data": "Завершить игру",
            },
        ],
    ]
    buttons = shares_buttons + option_buttons
    keyboard = json.dumps(
        {
            "inline_keyboard": buttons,
        }
    )
    return keyboard

async def info_keyboard_generator():
    keyboard = json.dumps(
        {
            "inline_keyboard": [
                [
                    {"text": "Привет биржа", "callback_data": "Привет биржа"},
                ],
                [
                    {"text": "Правила игры", "callback_data": "Правила игры"},
                ],
                [
                    {"text": "О боте", "callback_data": "О боте"},
                ],
                [
                    {"text": "Создать игру", "callback_data": "Кто будет играть?"}
                ],
                [
                    {"text": "Начать игру", "callback_data": "Начать игру"}
                ]
            ]
        }
    )
    return keyboard