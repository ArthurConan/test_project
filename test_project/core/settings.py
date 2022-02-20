import toml

from functools import lru_cache
from pathlib import Path
from pydantic import BaseSettings
from typing import List

ROOT = Path(__file__).resolve(strict=True).parent.parent.parent


class Server(BaseSettings):
    proto: str
    host: str
    port: int
    debug: bool
    cors_origins: List[str]
    cors_methods: List[str]
    cors_headers: List[str]


class Auth(BaseSettings):
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int


class Postgresql(BaseSettings):
    host: str
    port: int
    user: str
    password: str
    db: str


class Settings(BaseSettings):
    server: Server
    auth: Auth
    postgresql: Postgresql


def make_settings() -> Settings:
    parsed_settings = toml.load(Path(ROOT / "settings.toml"))
    return Settings(
        server=Server.parse_obj(parsed_settings["server"]),
        auth=Auth.parse_obj(parsed_settings["auth"]),
        postgresql=Postgresql.parse_obj(parsed_settings["postgresql"]),
    )


@lru_cache()
def get_settings():
    return make_settings()
