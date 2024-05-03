from aiohttp.web import (
    Application as AiohttpApplication,
)

from .config import setup_config
from .routes import setup_routes

__all__ = ("Application",)


class Application(AiohttpApplication):
    config = None
    store = None
    database = None


app = Application()


def setup_app(config_path: str) -> Application:
    setup_config(app)
    setup_routes(app)
    return app
