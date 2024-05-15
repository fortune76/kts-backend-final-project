import json
import typing

from aiohttp import TCPConnector
from aiohttp.client import ClientSession
from sqlalchemy import select

from app.base.base_accessor import BaseAccessor
from app.telegram.models import PollModel
from app.telegram.poller import Poller

if typing.TYPE_CHECKING:
    from app.web.app import Application


class TelegramAPIAccessor(BaseAccessor):
    def __init__(self, app: "Application", *args, **kwargs) -> None:
        super().__init__(app, *args, **kwargs)
        self.session: ClientSession | None = None
        self.poller: Poller | None = None
        self.message: str | None = None
        self.tg_api: str = f"https://api.telegram.org/bot{app.config.bot.token}"

    async def connect(self, app: "Application"):
        self.session = ClientSession(connector=TCPConnector(verify_ssl=False))
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
            params=params,
        ) as response:
            data = await response.json()
            self.logger.info(data)
            return data

    async def send_answer_callback_query(self, callback_query_id: int):
        async with self.session.post(
            self._build_query(host=self.tg_api, method="answerCallbackQuery"),
            json={
                "callback_query_id": callback_query_id,
            },
        ) as response:
            return await response.json()

    async def send_start_poll(self, chat_id: int, game_id: int):
        async with self.session.post(
            self._build_query(host=self.tg_api, method="sendpoll"),
            json={
                "chat_id": chat_id,
                "question": "Кто будет принимать участие в игре?",
                "options": [
                    {"text": "Буду"},
                    {"text": "Не буду"},
                ],
                "is_anonymous": False,
                "allows_multiple_answers": False,
                "type": "regular",
                "open_period": 60,
            },
        ) as response:
            result = await response.json()
            poll_id = result["result"]["poll"]["id"]
            await self.create_poll(poll_id=poll_id, game_id=game_id)
            return result

    async def get_poll_results(self, poll_id: str):
        async with self.session.post(
            self._build_query(host=self.tg_api, method="pollanswer"),
            json={
                "poll_id": poll_id,
            },
        ) as response:
            return await response.json()

    async def create_poll(self, poll_id: str, game_id: int):
        async with self.app.database.session() as session:
            poll = PollModel(
                poll_id=poll_id,
                game_id=game_id,
            )
            session.add(poll)
            await session.commit()
        return poll

    async def get_poll(self, poll_id: str):
        async with self.app.database.session() as session:
            stmt = select(PollModel).where(PollModel.poll_id == poll_id)
            return await session.scalar(stmt)

    async def send_message(self, chat_id: int, text: str):
        async with self.session.post(
                self._build_query(host=self.tg_api, method="sendMessage"),
                json={
                    "chat_id": chat_id,
                    "text": text,
                },
        ) as response:
            return await response.json()

    async def send_info_message_to_chat(self, chat_id: int, text: str, keyboard):
        async with self.session.post(
                self._build_query(host=self.tg_api, method="sendMessage"),
                json={
                    "chat_id": chat_id,
                    "text": text,
                    "parse_mode": "Markdown",
                    "reply_markup": keyboard,
                },
        ) as response:
            return await response.json()

    async def send_game_message(self, chat_id: int, text: str, keyboard):

        async with self.session.post(
            self._build_query(host=self.tg_api, method="sendMessage"),
            json={
                "chat_id": chat_id,
                "text": text,
                "parse_mode": "Markdown",
                "reply_markup": keyboard,
            },
        ) as response:
            return await response.json()

    async def edit_game_message(
        self,
        chat_id: int,
        message_id: int,
        text: str,
        keyboard,
    ):
        async with self.session.post(
            self._build_query(host=self.tg_api, method="editMessageText"),
            json={
                "chat_id": chat_id,
                "message_id": message_id,
                "text": text,
                "parse_mode": "Markdown",
                "reply_markup": keyboard,
            },
        ) as response:
            return await response.json()
