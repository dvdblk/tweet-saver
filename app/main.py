import asyncio

from app import init_logger
from app.config import Config
from app.discord_manager import DiscordManager
from app.twitter.streaming import TweetStreamingClient

log = init_logger(__name__)


async def main(cfg: Config):
    # Create manager for Discord
    discord = DiscordManager(
        webhook_url=config.discord_webhook_url
    )

    # Create tweet streaming client
    twitter = TweetStreamingClient(
        discord=discord,
        stream_rule=config.twitter_filtered_stream_rule,
        bearer_token=config.twitter_bearer_token,
    )

    # Start filtered stream based on the given stream rule
    await twitter.start_filtered_stream()


if __name__ == "__main__":
    config = Config()

    asyncio.run(main(config))
