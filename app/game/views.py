from aiohttp.web_exceptions import HTTPBadRequest
from aiohttp_apispec import request_schema, response_schema

from app.game.schemes import GameSchema
from app.web.mixins import ViewMixin


class GameView(ViewMixin):
    @request_schema(GameSchema)
    @response_schema(GameSchema)
    def get(self, request):
        try:
            data = self.request["data"]
        except KeyError:
            raise HTTPBadRequest

        game = self.request.app.store.games.get(data["game_id"])
        return json_response(GameSchema().dump(game))

    def post(self, request):
        