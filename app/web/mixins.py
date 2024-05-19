import typing

from aiohttp.abc import StreamResponse
from aiohttp.web import (
    Request as AiohttpRequest,
    View as AiohttpView,
)
from aiohttp.web_exceptions import HTTPUnauthorized
from aiohttp_session import get_session

from app.store import Store
from app.store.database.database import Database

if typing.TYPE_CHECKING:
    from app.web.app import Application


class Request(AiohttpRequest):
    @property
    def app(self) -> "Application":
        return super().app()


class View(AiohttpView):
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


class AuthRequiredMixin:
    async def _iter(self) -> StreamResponse:
        session = await get_session(self.request)
        try:
            session["admin"]
        except:
            raise HTTPUnauthorized
        return await super(AuthRequiredMixin, self)._iter()
