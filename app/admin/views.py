from aiohttp.web_exceptions import HTTPBadRequest, HTTPConflict, HTTPForbidden
from aiohttp_apispec import (
    docs,
    querystring_schema,
    request_schema,
    response_schema,
)
from aiohttp_session import new_session

from app.admin.schemes import (
    AdminSchema,
    GameChatIdSchema,
    GameIdSchema,
    GameListSchema,
    GameSchema,
    ListSettingsSchema,
    ListShareSchema,
    MaximumSharePriceSchema,
    MinimalSharePriceSchema,
    PlayerBalanceSchema,
    ShareNameSchema,
    ShareSchema,
    TurnCounterSchema,
    TurnTimerSchema,
    UserIdSchema,
    UserListSchema,
    UserSchema,
)
from app.web.mixins import AuthRequiredMixin, View
from app.web.utils import json_response


class AdminLoginView(View):
    @docs(
        tag=["admin"],
        summary="Admin login",
        description="Login admin to server",
    )
    @request_schema(AdminSchema)
    @response_schema(AdminSchema, 200)
    async def post(self):
        try:
            telegram_id = self.request["data"]["telegram_id"]
            password = self.request["data"]["password"]
        except KeyError:
            raise HTTPBadRequest

        is_admin = await self.store.user.is_admin(telegram_id=telegram_id)
        if not is_admin:
            raise HTTPForbidden

        check_credentials = await self.store.user.check_admin(
            telegram_id=telegram_id,
            password=password,
        )
        if not check_credentials:
            raise HTTPForbidden

        app = self.request.app
        admin = await app.store.user.get_admin_by_telegram_id(
            telegram_id=telegram_id
        )
        session = await new_session(request=self.request)
        raw_admin = AdminSchema().dump(admin)
        session["admin"] = raw_admin
        return json_response(data=AdminSchema().dump(admin))


class UserListView(AuthRequiredMixin, View):
    @docs(
        tags=["users"],
        summary="List of all users",
        description="List of all users who registered at bot",
    )
    @response_schema(UserListSchema)
    async def get(self):
        users = await self.store.user.get_users_list()
        return json_response(UserListSchema().dump({"users": users}))


class UserDetailView(AuthRequiredMixin, View):
    @docs(tags=["users"], summary="User details", description="User details")
    @querystring_schema(UserIdSchema)
    @response_schema(UserSchema)
    async def get(self):
        try:
            user_id = int(self.request.query["id"])
        except KeyError:
            raise HTTPBadRequest

        user = await self.store.user.get_user_by_id(user_id)
        return json_response(UserSchema().dump(user))


class GameListView(AuthRequiredMixin, View):
    @docs(
        tags=["games"],
        summary="List of all games",
        description="List of all games that were played at bot",
    )
    @response_schema(GameListSchema)
    async def get(self):
        games = await self.store.games.get_all_finished_games()
        return json_response(GameListSchema().dump({"games": games}))


class GameDetailView(AuthRequiredMixin, View):
    @docs(
        tags=["games"],
        summary="Game detail view",
        description="Information about a specific game",
    )
    @querystring_schema(GameIdSchema)
    @response_schema(GameSchema)
    async def get(self):
        try:
            game_id = int(self.request.query["id"])
        except KeyError:
            raise HTTPBadRequest

        game = await self.store.games.get_game_by_id(game_id)
        return json_response(GameSchema().dump(game))


class LastChatGameView(AuthRequiredMixin, View):
    @docs(
        tags=["games"],
        summary="Last chat game",
        description="Get last chat game by chat id",
    )
    @querystring_schema(GameChatIdSchema)
    @response_schema(GameSchema)
    async def get(self):
        try:
            chat_id = int(self.request.query["chat_id"])
        except KeyError:
            raise HTTPBadRequest
        game = await self.store.games.get_last_chat_game(chat_id)
        return json_response(GameSchema().dump(game))


class ShareView(AuthRequiredMixin, View):
    @docs(
        tags=["settings"],
        summary="Add share",
        description="Add share to game database",
    )
    @request_schema(ShareSchema)
    @response_schema(ShareSchema)
    async def post(self):
        try:
            data = self.request["data"]
        except KeyError:
            raise HTTPBadRequest

        share_exists = await self.store.games.get_share_by_name(data["name"])
        if share_exists:
            raise HTTPConflict
        share = await self.store.games.create_share(data["name"], data["price"])
        return json_response(ShareSchema().dump(share))

    @docs(
        tags=["settings"],
        summary="Delete share",
        description="Delete share from game database",
    )
    @querystring_schema(ShareNameSchema)
    async def delete(self):
        try:
            name = self.request.query["name"]
        except KeyError:
            raise HTTPBadRequest
        share_exists = await self.store.games.get_share_by_name(name)
        if not share_exists:
            raise HTTPBadRequest
        await self.store.games.delete_share(share_exists.id)
        return json_response(ShareSchema().dump(share_exists))


class ListShareView(AuthRequiredMixin, View):
    @docs(
        tags=["settings"],
        summary="List of bot shares",
        description="List of shares that available in the game",
    )
    @response_schema(ListShareSchema)
    async def get(self):
        shares = await self.store.games.get_shares()
        return json_response(ListShareSchema().dump({"shares": shares}))


class TurnTimerView(AuthRequiredMixin, View):
    @docs(
        tags=["settings"],
        summary="Update turn timer",
        description="Update turn timer if there are no active games",
    )
    @request_schema(TurnTimerSchema)
    @response_schema(TurnTimerSchema)
    async def post(self):
        try:
            turn_timer = self.request["data"]["turn_timer"]
        except KeyError:
            raise HTTPBadRequest

        games = await self.store.games.get_all_active_games()
        if games:
            return json_response(
                {
                    "message": "Не возможно изменить настройки. Есть активная игра"
                }
            )
        await self.store.settings.update_turn_timer(turn_timer)
        return json_response(TurnTimerSchema().dump({"turn_timer": turn_timer}))


class TurnCounterView(AuthRequiredMixin, View):
    @docs(
        tags=["settings"],
        summary="Update turn counter",
        description="Update turn counter if there are no active games",
    )
    @request_schema(TurnCounterSchema)
    @response_schema(TurnCounterSchema)
    async def post(self):
        try:
            turn_counter = self.request["data"]["turn_counter"]
        except KeyError:
            raise HTTPBadRequest

        games = await self.store.games.get_all_active_games()
        if games:
            return json_response(
                {
                    "message": "Не возможно изменить настройки. Есть активная игра"
                }
            )
        await self.store.settings.update_turn_counter(turn_counter)
        return json_response(
            TurnCounterSchema().dump({"turn_counter": turn_counter})
        )


class PlayerBalanceView(AuthRequiredMixin, View):
    @docs(
        tags=["settings"],
        summary="Update player balance",
        description="Update player balance if there are no active games",
    )
    @request_schema(PlayerBalanceSchema)
    @response_schema(PlayerBalanceSchema)
    async def post(self):
        try:
            player_balance = self.request["data"]["player_balance"]
        except KeyError:
            raise HTTPBadRequest

        games = await self.store.games.get_all_active_games()
        if games:
            return json_response(
                {
                    "message": "Не возможно изменить настройки. Есть активная игра"
                }
            )
        await self.store.settings.update_player_balance(player_balance)
        return json_response(
            PlayerBalanceSchema().dump({"player_balance": player_balance})
        )


class MinimalSharePriceView(AuthRequiredMixin, View):
    @docs(
        tags=["settings"],
        summary="Update minimal share price",
        description="Update minimal share price if there are no active games",
    )
    @request_schema(MinimalSharePriceSchema)
    @response_schema(MinimalSharePriceSchema)
    async def post(self):
        try:
            minimal_share_price = self.request["data"]["minimal_share_price"]
        except KeyError:
            raise HTTPBadRequest

        games = await self.store.games.get_all_active_games()
        if games:
            return json_response(
                {
                    "message": "Не возможно изменить настройки. Есть активная игра"
                }
            )
        await self.store.settings.update_shares_minimal_price(minimal_share_price)
        return json_response(
            MinimalSharePriceSchema().dump(
                {"minimal_share_price": minimal_share_price}
            )
        )


class MaximumSharePriceView(AuthRequiredMixin, View):
    @docs(
        tags=["settings"],
        summary="Update minimal share price",
        description="Update minimal share price if there are no active games",
    )
    @request_schema(MaximumSharePriceSchema)
    @response_schema(MaximumSharePriceSchema)
    async def post(self):
        try:
            maximum_share_price = self.request["data"]["maximum_share_price"]
        except KeyError:
            raise HTTPBadRequest

        games = await self.store.games.get_all_active_games()
        if games:
            return json_response(
                {
                    "message": "Не возможно изменить настройки. Есть активная игра"
                }
            )
        await self.store.settings.update_shares_maximum_price(maximum_share_price)
        return json_response(
            MaximumSharePriceSchema().dump(
                {"maximum_share_price": maximum_share_price}
            )
        )


class ListSettingsView(AuthRequiredMixin, View):
    @docs(
        tags=["settings"],
        summary="List of game settings",
        description="List of game settings",
    )
    @response_schema(ListSettingsSchema)
    async def get(self):
        turn_timer = await self.store.settings.get_turn_timer()
        turn_counter = await self.store.settings.get_turn_counter()
        player_balance = await self.store.settings.get_player_balance()
        minimal_share_price = (
            await self.store.settings.get_shares_minimal_price()
        )
        maximum_share_price = (
            await self.store.settings.get_shares_maximum_price()
        )
        response = {
            "turn_timer": turn_timer,
            "turn_counter": turn_counter,
            "player_balance": player_balance,
            "minimal_share_price": minimal_share_price,
            "maximum_share_price": maximum_share_price,
        }
        return json_response(ListSettingsSchema().dump(response))
