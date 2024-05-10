from collections.abc import Iterable

from app.game.models import (
    GameInventoryModel,
    GameModel,
    PlayerInventoryModel,
    PlayerModel,
    ShareModel,
)
from app.users.models import UserModel


def user_to_dict(user: UserModel) -> dict:
    return {
        "id": user.id,
        "telegram_id": user.telegram_id,
        "nickname": user.nickname,
        "first_name": user.first_name,
        "is_admin": user.is_admin,
        "password": user.password,
    }


def users_to_dict(users: Iterable[UserModel]) -> list[dict]:
    return [user_to_dict(user) for user in users]


def game_to_dict(game: GameModel) -> dict:
    return {
        "id": game.id,
        "chat_id": game.chat_id,
        "started_at": game.started_at,
        "finish_at": game.finish_at,
        "is_active": game.is_active,
        "last_turn": game.last_turn,
    }


def player_to_dict(player: PlayerModel) -> dict:
    return {
        "id": player.id,
        "user_id": player.user_id,
        "balance": player.balance,
        "alive": player.alive,
        "game_id": player.game_id,
    }


def share_to_dict(share: ShareModel) -> dict:
    return {
        "id": share.id,
        "name": share.name,
        "start_price": share.start_price,
    }


def game_inventory_to_dict(
    game_inventory: list[GameInventoryModel],
) -> list[dict]:
    return [
        {
            "share_id": game_item.share_id,
            "game_id": game_item.game_id,
            "price": game_item.price,
        }
        for game_item in game_inventory
    ]


def player_inventory_to_dict(
    player_inventory: list[PlayerInventoryModel],
) -> list[dict]:
    return [
        {
            "id": player_item.id,
            "share_id": player_item.share_id,
            "share_owner": player_item.share_owner,
        }
        for player_item in player_inventory
    ]
