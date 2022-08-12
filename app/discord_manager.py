from aiohttp import ClientSession
from discord import (
    AsyncWebhookAdapter,
    Webhook,
)


class DiscordManager:
    """Manage sending messages to a Discord channel"""

    def __init__(self, webhook_url: str) -> None:
        self.discord: Webhook = Webhook.from_url(
            webhook_url,
            adapter=AsyncWebhookAdapter(ClientSession()),
        )

    async def send_new_tweet(self, tweet_url: str):
        # TODO: Finish with embed
        await self.discord.send(tweet_url)
