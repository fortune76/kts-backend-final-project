import asyncio
from asyncio import Future, Task

from app.store import Store
from app.telegram.bot import Bot


class Poller:
    def __init__(self, store: Store) -> None:
        self.store = store
        self.is_running = False
        self.poll_task: Task | None = None
        self.bot: Bot | None = None
        self.queue: asyncio.Queue[Task] | None = None

    def _done_callback(self, result: Future) -> None:
        if result.exception():
            self.store.app.logger.exception(
                "poller stopped with exception", exc_info=result.exception()
            )
        if self.is_running:
            self.start()

    def start(self) -> None:
        self.bot = Bot(self.store)
        self.queue = self.bot.queue
        self.is_running = True
        self.poll_task = asyncio.create_task(self.poll())
        self.poll_task.add_done_callback(self._done_callback)

    async def stop(self) -> None:
        self.is_running = False
        await self.poll_task

    async def poll(self) -> None:
        offset = 0
        while self.is_running:
            message = await self.store.telegram_api.poll(
                offset=offset, timeout=5
            )
            for item in message["result"]:
                await self.queue.put(
                    asyncio.create_task(self.bot.parse_message(item))
                )
                offset = item["update_id"] + 1
