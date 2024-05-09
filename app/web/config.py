import typing
from dataclasses import dataclass

import yaml

if typing.TYPE_CHECKING:
    from app.web.app import Application


@dataclass
class SessionConfig:
    key: str


@dataclass
class AdminConfig:
    telegram_id: int
    password: str
    nickname: str
    first_name: str
    is_admin: bool
    password: str | None


@dataclass
class BotConfig:
    token: str


@dataclass
class DatabaseConfig:
    host: str
    port: int
    user: str
    password: str
    database: str


@dataclass
class Config:
    admin: AdminConfig
    session: SessionConfig | None = None
    bot: BotConfig | None = None
    database: DatabaseConfig | None = None


def setup_config(app: "Application", config_path: str):
    with open(config_path, "r") as f:
        raw_config = yaml.safe_load(f)

    app.config = Config(
        # session=SessionConfig(
        #     key=raw_config["session"]["key"],
        # ),
        admin=AdminConfig(
            telegram_id=raw_config["admin"]["telegram_id"],
            password=str(raw_config["admin"]["password"]),
            nickname=raw_config["admin"]["nickname"],
            first_name=raw_config["admin"]["first_name"],
            is_admin=raw_config["admin"]["is_admin"],
        ),
        bot=BotConfig(
            token=raw_config["bot"]["token"],
        ),
        database=DatabaseConfig(**raw_config["database"]),
    )
