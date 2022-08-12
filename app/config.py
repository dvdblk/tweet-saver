from typing import List

from pydantic import (
    AnyHttpUrl,
    BaseSettings,
)


class Config(BaseSettings):
    discord_webhook_url: AnyHttpUrl

    twitter_bearer_token: str

    twitter_filtered_stream_rule: str
