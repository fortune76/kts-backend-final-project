import json


def game_keyboard_generator(data: list) -> str:
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
        [
            {
                "text": "Пропустить ход",
                "callback_data": "Пропустить ход",
            }
        ],
    ]
    buttons = shares_buttons + option_buttons
    return json.dumps(
        {
            "inline_keyboard": buttons,
        }
    )


def info_keyboard_generator() -> str:
    return json.dumps(
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
                    {
                        "text": "Создать игру",
                        "callback_data": "Кто будет играть?",
                    }
                ],
                [{"text": "Начать игру", "callback_data": "Начать игру"}],
            ]
        }
    )


def get_admin_keyboard(setting_type: str) -> str | None:
    if setting_type == "turn_timer":
        return json.dumps(
            {
                "inline_keyboard": [
                    [{"text": f"{num}", "callback_data": f"turn_timer {num}"}]
                    for num in range(15, 91, 15)
                ]
            }
        )
    elif setting_type == "turn_counter":
        return json.dumps(
            {
                "inline_keyboard": [
                    [{"text": f"{num}", "callback_data": f"turn_counter {num}"}]
                    for num in range(2, 11, 2)
                ]
            }
        )
    elif setting_type == "player_balance":
        return json.dumps(
            {
                "inline_keyboard": [
                    [
                        {
                            "text": f"{num}",
                            "callback_data": f"player_balance {num}",
                        }
                    ]
                    for num in range(500, 2501, 500)
                ]
            }
        )
    elif setting_type == "share_minimal_price":
        return json.dumps(
            {
                "inline_keyboard": [
                    [
                        {
                            "text": f"{num}",
                            "callback_data": f"share_minimal_price {num}",
                        }
                    ]
                    for num in range(0, 2, 1)
                ]
            }
        )
    elif setting_type == "share_maximum_price":
        return json.dumps(
            {
                "inline_keyboard": [
                    [
                        {
                            "text": f"{num}",
                            "callback_data": f"share_maximum_price {num}",
                        }
                    ]
                    for num in range(500, 2501, 500)
                ]
            }
        )
    return None


def get_main_admin_keyboard() -> str:
    return json.dumps(
        {
            "inline_keyboard": [
                [
                    {
                        "text": "Изменить максимальное количество ходов",
                        "callback_data": "turn_counter",
                    },
                ],
                [
                    {
                        "text": "Изменить время хода",
                        "callback_data": "turn_timer",
                    },
                ],
                [
                    {
                        "text": "Изменить стартовый баланс игроков",
                        "callback_data": "player_balance",
                    },
                ],
                [
                    {
                        "text": "Изменить минимальную стоимость акции",
                        "callback_data": "share_minimal_price",
                    }
                ],
                [
                    {
                        "text": "Изменить максимальную стоимость акции",
                        "callback_data": "share_maximum_price",
                    }
                ],
            ]
        }
    )
