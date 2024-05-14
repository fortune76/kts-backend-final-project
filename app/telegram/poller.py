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

    def _done_callback(self, result: Future) -> None:
        if result.exception():
            self.store.app.logger.exception(
                "poller stopped with exception", exc_info=result.exception()
            )
        if self.is_running:
            self.start()

    def start(self) -> None:
        self.bot = Bot(self.store)
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
                if item.get("message"):
                    if item["message"].get("new_chat_participant"):
                        pass
                    else:
                        await self.bot.check_message(
                            item["message"]["chat"]["id"],
                            item["message"]["text"],
                        )
                elif item.get("poll"):
                    await self.store.telegram_api.get_poll_results(
                        item["poll"]["id"]
                    )
                elif item.get("poll_answer"):
                    if item["poll_answer"]["option_ids"][0] == 0:
                        user = await self.bot.create_user(
                            telegram_id=item["poll_answer"]["user"]["id"],
                            nickname=item["poll_answer"]["user"]["username"],
                            first_name=item["poll_answer"]["user"]["first_name"],
                        )
                        game_id = (
                            await self.store.telegram_api.get_poll(
                                poll_id=item["poll_answer"]["poll_id"],
                            )
                        ).game_id
                        if user:
                            user_id = user.id
                        else:
                            user_id = (
                                await self.store.user.get_user_by_telegram_id(
                                    item["poll_answer"]["user"]["id"]
                                )
                            ).id
                        await self.bot.create_player(
                            user_id=user_id,
                            game_id=game_id,
                        )
                elif item.get("edited_message"):
                    pass
                else:
                    await self.bot.check_message(
                        item["callback_query"]["message"]["chat"]["id"],
                        item["callback_query"]["data"],
                        item["callback_query"]["from"]["id"],
                        item["callback_query"]["message"]["message_id"],
                    )
                    await self.store.telegram_api.send_answer_callback_query(
                        item["callback_query"]["id"],
                    )
