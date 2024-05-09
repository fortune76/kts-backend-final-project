from marshmallow import Schema, fields

class GameSchema(Schema):
    id = fields.Integer(required=False)
    chat_id = fields.Integer(required=True)
    started_at = fields.DateTime(required=False)
    finish_at = fields.DateTime(required=False)
    is_active = fields.Boolean(required=False)
    last_turn = fields.Integer(required=False)

class PlayerSchema(Schema):
    id = fields.Integer(required=False)
    user_id = fields.Integer(required=True)
    game_id = fields.Integer(required=True)
    balance = fields.Integer(required=False)
    alive = fields.Boolean(required=False)

class ShareSchema(Schema):
    id = fields.Integer(required=False)
    name = fields.String(required=True)
    start_price = fields.Integer(required=True)
