from typing import List

from pydantic import (
    AnyHttpUrl,
    BaseSettings,
)


class Config(BaseSettings):
    # URL for posting to a Discord channel via Webhooks
    discord_webhook_url: AnyHttpUrl

    # Twitter API v2 bearer token
    twitter_bearer_token: str

    # Twitter Stream Rule for filtering tweet streams
    # For more: https://developer.twitter.com/en/docs/twitter-api/tweets/filtered-stream/integrate/build-a-rule
    twitter_filtered_stream_rule: str
