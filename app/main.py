import asyncio

from app import init_logger
from app.config import Config
from app.discord_manager import DiscordManager
from app.twitter import TweetStreamingClient

log = init_logger(__name__)


async def main(cfg: Config):
    discord = DiscordManager(
        webhook_url=config.discord_webhook_url
    )

    twitter = TweetStreamingClient(
        discord=discord,
        stream_rule=config.twitter_filtered_stream_rule,
        bearer_token=config.twitter_bearer_token,
    )

    await twitter.start_filtered_stream()


if __name__ == "__main__":
    config = Config()

    asyncio.run(main(config))
