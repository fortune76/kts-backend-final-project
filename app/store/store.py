import typing

from app.store.database.database import Database

if typing.TYPE_CHECKING:
    from app.web.app import Application


class Store:
    def __init__(self, app: "Application", *args, **kwargs):
        from app.game.accessor import GameAccessor
        from app.telegram.accessor import TelegramAPIAccessor
        from app.users.accessor import UserAccessor

        self.app = app
        self.user = UserAccessor(app)
        self.telegram_api = TelegramAPIAccessor(app)
        self.games = GameAccessor(app)


def setup_store(app: "Application"):
    app.database = Database(app)
    app.on_startup.append(app.database.connect)
    app.on_cleanup.append(app.database.disconnect)
    app.store = Store(app)
