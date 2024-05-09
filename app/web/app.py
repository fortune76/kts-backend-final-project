from aiohttp.web import (
    Application as AiohttpApplication,
)

from app.store.store import Store, setup_store

from .config import Config, setup_config
from .routes import setup_routes

__all__ = ("Application", "setup_app")

from app.store.database.database import Database


class Application(AiohttpApplication):
    config: Config | None = None
    store: Store | None = None
    database: Database | None = None


app = Application()


def setup_app(config_path: str) -> Application:
    setup_config(app, config_path)
    setup_routes(app)
    setup_store(app)
    return app
