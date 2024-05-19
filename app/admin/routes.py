import typing

if typing.TYPE_CHECKING:
    from app.web.app import Application

from app.admin.views import (
    AdminLoginView,
    UserListView,
    UserDetailView,
    GameListView,
    GameDetailView,
    LastChatGameView,
    ShareView,
    ListShareView,
    ListSettingsView,
    TurnTimerView,
    TurnCounterView,
    PlayerBalanceView,
    MinimalSharePriceView,
    MaximumSharePriceView,
)

def setup_routes(app: "Application"):
    app.router.add_view("/admin/login", AdminLoginView)
    app.router.add_view("/admin/user/user_list", UserListView)
    app.router.add_view("/admin/user/user_detail", UserDetailView)
    app.router.add_view("/admin/game/games_list", GameListView)
    app.router.add_view("/admin/game/game_detail", GameDetailView)
    app.router.add_view("/admin/game/chat_last_game", LastChatGameView)
    app.router.add_view("/admin/settings/share", ShareView)
    app.router.add_view("/admin/settings/shares_list", ListShareView)
    app.router.add_view("/admin/settings", ListSettingsView)
    app.router.add_view("/admin/settings/turn_timer", TurnTimerView)
    app.router.add_view("/admin/settings/turn_counter", TurnCounterView)
    app.router.add_view("/admin/settings/player_balance", PlayerBalanceView)
    app.router.add_view("/admin/settings/minimal_share_price", MinimalSharePriceView)
    app.router.add_view("/admin/settings/maximum_share_price", MaximumSharePriceView)