from marshmallow import Schema, fields


class AdminSchema(Schema):
    telegram_id = fields.Integer(required=True)
    password = fields.Str(required=True)


class AdminResponseSchema(Schema):
    telegram_id = fields.Integer(required=True)


class UserSchema(Schema):
    id = fields.Integer(required=True)
    telegram_id = fields.Integer(required=True)
    username = fields.String(required=True)
    nickname = fields.String(required=True)
    is_admin = fields.Boolean(required=True)
    password = fields.String(required=True)


class UserIdSchema(Schema):
    id = fields.Integer(required=True)


class UserListSchema(Schema):
    users = fields.Nested(UserSchema, many=True)


class GameSchema(Schema):
    id = fields.Integer(required=True)
    chat_id = fields.Integer(required=True)
    started_at = fields.DateTime(required=True)
    finish_at = fields.DateTime(required=True)
    is_active = fields.Boolean(required=True)


class GameIdSchema(Schema):
    id = fields.Integer(required=True)


class GameChatIdSchema(Schema):
    chat_id = fields.Integer(required=True)


class GameListSchema(Schema):
    games = fields.Nested(GameSchema, many=True)


class ShareSchema(Schema):
    id = fields.Integer(required=False)
    name = fields.String(required=True)
    price = fields.Integer(required=True)


class ShareNameSchema(Schema):
    name = fields.String(required=True)


class ListShareSchema(Schema):
    shares = fields.Nested(ShareSchema, many=True)


class TurnTimerSchema(Schema):
    turn_timer = fields.Integer(required=True)


class TurnCounterSchema(Schema):
    turn_counter = fields.Integer(required=True)


class PlayerBalanceSchema(Schema):
    player_balance = fields.Integer(required=True)


class MinimalSharePriceSchema(Schema):
    minimal_share_price = fields.Integer(required=True)


class MaximumSharePriceSchema(Schema):
    maximum_share_price = fields.Integer(required=True)


class ListSettingsSchema(Schema):
    turn_timer = fields.Integer(required=True)
    turn_counter = fields.Integer(required=True)
    player_balance = fields.Integer(required=True)
    minimal_share_price = fields.Integer(required=True)
    maximum_share_price = fields.Integer(required=True)
