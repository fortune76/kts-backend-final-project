import typing

if typing.TYPE_CHECKING:
    from app.web.app import Application


class Store:
    def __init__(self, app: "Application", *args, **kwargs):
        from app.telegram.accessor import TelegramAPIAccessor
        from app.users.accessor import UserAccessor

        self.app = app
        self.user = UserAccessor(self)
        self.telegram_api = TelegramAPIAccessor(app)


def setup_store(app: "Application"):
    app.store = Store(app)
