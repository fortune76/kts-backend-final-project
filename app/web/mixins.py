from aiohttp.web import (
    Request as AiohttpRequest,
    View as AiohttpView,
)

from app.store import Store
from app.store.database.database import Database
from app.web.app import Application


class Request(AiohttpRequest):
    @property
    def app(self) -> Application:
        return super().app()

class ViewMixin(AiohttpView):
    @property
    def request(self) -> Request:
        return super().request

    @property
    def database(self) -> Database:
        return self.request.app.database

    @property
    def store(self) -> Store:
        return self.request.app.store

    @property
    def data(self) -> dict:
        return self.request.get("data", {})

class AdminOnlyMixin:
    # TODO: сделать авторизацию админа
    pass