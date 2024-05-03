import typing
from aiohttp import TCPConnector
from aiohttp.client import ClientSession
from urllib.parse import urljoin

from app.base.base_accessor import BaseAccessor
from app.telegram.poller import Poller

if typing.TYPE_CHECKING:
    from app.web.app import Application


class TelegramAPIAccessor(BaseAccessor):

    def __init__(self, app: "Application", *args, **kwargs) -> None:
        super().__init__(app, *args, **kwargs)
        self.session: ClientSession | None = None
        self.message: str | None = None
        self.tg_api: str = f"https://api.telegram.org/bot{app.config.bot.token}"
    
    async def connect(self, app: "Application"):
        self.session = ClientSession(connector=TCPConnector(verify_ssl=False))
        # try:
        #     await self.poll()
        # except Exception as e:
        #     self.logger.error("Exception", exc_info=e)

        self.poller = Poller(app.store)
        self.logger.info("start polling")
        self.poller.start()

    async def disconnect(self, app: "Application"):
        if self.session:
            await self.session.close()

        if self.poller:
            await self.poller.stop()

    @staticmethod
    def _build_query(host: str, method: str):
        return f"{host}/{method}"
    
    async def poll(self, offset: int | None = None, timeout: int = 0) -> None:
        params = {
            "timeout": timeout,
            "offset": offset,
        }
        async with self.session.get(
            self._build_query(
                host=self.tg_api,
                method="getUpdates",
            ),
            params=params
        ) as response:
            data = await response.json()
            self.logger.info(data)
            return data
    
    async def send_message(self, chat_id: int, text: str):
        async with self.session.post(
            self._build_query(
                host=self.tg_api,
                method="sendMessage"
            ),
            json={
                "chat_id": chat_id,
                "text": text,
            }
        ) as response:
            data = await response.json()
            return data