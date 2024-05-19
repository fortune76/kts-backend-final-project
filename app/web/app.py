import base64

from cryptography.fernet import Fernet

from aiohttp.web import (
    Application as AiohttpApplication,
)
from aiohttp_apispec import setup_aiohttp_apispec
from aiohttp_session.cookie_storage import EncryptedCookieStorage

from app.store.store import Store, setup_store

from .config import Config, setup_config
from .mw import setup_middlewares
from .routes import setup_routes

from aiohttp_session import setup as session_setup

__all__ = ("Application", "setup_app")

from app.store.database.database import Database


class Application(AiohttpApplication):
    config: Config | None = None
    store: Store | None = None
    database: Database | None = None


app = Application()


def setup_app(config_path: str) -> Application:
    fernet_key = Fernet.generate_key()
    secret_key = base64.urlsafe_b64decode(fernet_key)
    setup_config(app, config_path)
    setup_routes(app)
    setup_aiohttp_apispec(
        app, title="Exchange bot", url="/docs/json", swagger_path="/docs"
    )
    session_setup(app, EncryptedCookieStorage(secret_key))
    setup_middlewares(app)
    setup_store(app)
    return app
