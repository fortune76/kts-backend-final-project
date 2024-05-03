import asyncio
from asyncio import Future, Task

from app.store import Store


class Poller:
    def __init__(self, store: Store) -> None:
        self.store = store
        self.is_running = False
        self.poll_task: Task | None = None

    def _done_callback(self, result: Future) -> None:
        if result.exception():
            self.store.app.logger.exception(
                "poller stopped with exception", exc_info=result.exception()
            )
        if self.is_running:
            self.start()

    def start(self) -> None:
        self.is_running = True
        self.poll_task = asyncio.create_task(self.poll())
        self.poll_task.add_done_callback(self._done_callback)

    async def stop(self) -> None:
        self.is_running = False
        await self.poll_task

    async def poll(self) -> None:
        offset = 0
        while self.is_running:
            res = await self.store.telegram_api.poll(offset=offset, timeout=5)
            for item in res["result"]:
                offset = item["update_id"] + 1
                await self.store.telegram_api.send_message(
                    item["message"]["chat"]["id"], item["message"]["text"]
                )
