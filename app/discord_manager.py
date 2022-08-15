from typing import List

from aiohttp import ClientSession
from discord import (
    AsyncWebhookAdapter,
    Embed,
    Webhook,
)


class DiscordManager:
    """Manage sending messages to a Discord channel"""
    # URL to display in the footer of every Embed
    FOOTER_URL = "https://img.icons8.com/color/48/000000/twitter--v1.png"

    def __init__(self, webhook_url: str) -> None:
        self.discord: Webhook = Webhook.from_url(
            webhook_url,
            adapter=AsyncWebhookAdapter(ClientSession()),
        )

    def _add_media_embeds(
            self, url: str, media_urls: List[str],
            embeds: List[Embed]
        ) -> List[Embed]:
        """Add an Embed for each media_url.

        Note:
            If the embeds param already contains an Embed, the first image
            is added to this embed instead of creating a new Embed.
        """
        n_images = min(len(media_urls), 4)
        if n_images > 0:
            # Add image to existing embed
            embeds[0].set_image(url=media_urls[0])

        # Add Embed for each media URL
        if n_images > 1:
            for i in range(1, n_images):
                img_embed = Embed(url=url)
                img_embed.set_image(url=media_urls[i])
                embeds.append(img_embed)

        return embeds

    async def send_tweet_embed(
        self, url: str, text: str, created_at: str,
        username: str, name: str, author_image_url: str,
        media_urls: List[str] = []
    ) -> None:
        """Send embed of a normal tweet to Discord"""
        embeds = []
        embed = Embed(
            color=3370953,
            url=url,
            description=text
        )
        embed.set_author(
            name=f"{name} (@{username})",
            url=url,
            icon_url=author_image_url,
        )
        embed.set_footer(
            text=created_at,
            icon_url=self.FOOTER_URL
        )
        # Save first embed
        embeds.append(embed)

        # Add media
        embeds = self._add_media_embeds(
            url=url, media_urls=media_urls, embeds=embeds
        )

        await self.discord.send(embeds=embeds)

    async def send_retweet_embed(
        self, url: str, created_at: str, username: str,
        name: str, author_image_url: str,
        rt_name: str, rt_username: str, rt_text: str,
        rt_media_urls: List[str] = []
    ) -> None:
        """Send embed of a retweet to Discord"""
        embeds = []
        embed = Embed(
            color=40473,
            url=url,
        )
        embed.set_author(
            name=f"🔁 {name} (@{username}) retweeted",
            url=url,
            icon_url=author_image_url,
        )
        embed.add_field(
            name=f"> {rt_name} (@{rt_username})",
            value=f"> {rt_text}"
        )
        embed.set_footer(
            text=created_at,
            icon_url=self.FOOTER_URL
        )
        # Save first embed
        embeds.append(embed)

        # Add media
        embeds = self._add_media_embeds(
            url=url, media_urls=rt_media_urls, embeds=embeds
        )

        await self.discord.send(embeds=embeds)

    async def send_quote_tweet_embed(
        self, url: str, text: str, created_at: str, username: str,
        name: str, author_image_url: str,
        rt_name: str, rt_username: str, rt_text: str,
        media_urls: List[str] = []
    ) -> None:
        """Send embed of a quote tweet to Discord"""
        embeds = []
        embed = Embed(
            color=11468877,
            description=text
        )
        embed.set_author(
            name=f"{name} (@{username})",
            url=url,
            icon_url=author_image_url,
        )
        embed.add_field(
            name=f"> {rt_name} (@{rt_username})",
            value=f"> {rt_text}"
        )
        embed.set_footer(
            text=created_at,
            icon_url=self.FOOTER_URL
        )
        # Save first embed
        embeds.append(embed)

        # Add media
        embeds = self._add_media_embeds(
            url=url, media_urls=media_urls, embeds=embeds
        )

        await self.discord.send(embeds=embeds)

    async def send_reply_tweet_embed(
        self, url: str, text: str, created_at: str, username: str,
        name: str, author_image_url: str,
        rt_name: str, rt_username: str, rt_text: str,
        media_urls: List[str] = []
    ) -> None:
        """Send embed of a reply tweet to Discord"""
        embeds = []
        embed = Embed(
            color=57599,
            description=text
        )
        embed.set_author(
            name=f"↪️ {name} (@{username}) replied",
            url=url,
            icon_url=author_image_url,
        )
        embed.add_field(
            name=f"> {rt_name} (@{rt_username})",
            value=f"> {rt_text}"
        )
        embed.set_footer(
            text=created_at,
            icon_url=self.FOOTER_URL
        )
        # Save first embed
        embeds.append(embed)

        # Add media
        embeds = self._add_media_embeds(
            url=url, media_urls=media_urls, embeds=embeds
        )

        await self.discord.send(embeds=embeds)
