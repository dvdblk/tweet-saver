import re

from html import unescape
from typing import List, Optional

from aiohttp import ClientSession
from discord import (
    AsyncWebhookAdapter,
    Embed,
    Webhook,
)

from app.twitter.model import TweetData

def fmt_tweet_text(tweet_text: str, use_blockquote: bool = True) -> str:
    """Format the text in a tweet to display properly in a Discord Embed

    Args:
        use_blockquote (bool): if True, blockquotes will be added to
                                every line in `tweet_text`
                                (default value: `True`)
    """
    # Ensure that the HTML Encoded text from Twitter API
    # is changed properly for Discord embeds.
    # 1. unescape HTML
    tweet_text = unescape(tweet_text)
    # 2. escape asterisks and blockquotes
    tweet_text = re.sub("\*", "\\*", tweet_text)
    tweet_text = re.sub(">", "\>", tweet_text)
    # 3. add hyperlinks to (@<username>)
    tweet_text = re.sub("@(\w{1,15})", "[@\\1](https://twitter.com/\\1)", tweet_text)
    if use_blockquote:
        # 4. add '> ' after every \n
        # Also handles the case with multiple newlines
        tweet_text = re.sub("\n(.)|\n\n", "\n> \\1", tweet_text)
        # 5. add '> ' at the start
        tweet_text = f"> {tweet_text}"

    return tweet_text


class DiscordManager:
    """Manage sending messages to a Discord channel"""
    # Default footer URL to display when profile picture is not available
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

    def _add_ref_tweet(
        self, embed: Embed, ref_tweet_data: Optional[TweetData],
        text: str
    ):
        """Add reference tweet data to `Embed`"""
        if ref_tweet_data is not None:
            embed.add_field(
                name=f"> {ref_tweet_data.name} (@{ref_tweet_data.username})",
                value=fmt_tweet_text(ref_tweet_data.text)
            )
        else:
            embed.add_field(
                name="> Unknown",
                value=fmt_tweet_text(text)
            )

    async def send_tweet_embed(
        self, url: str, text: str, created_at: str,
        username: str, name: str, author_image_url: Optional[str],
        media_urls: List[str] = []
    ) -> None:
        """Send embed of a normal tweet to Discord"""
        embeds = []
        embed = Embed(
            color=5021419,
            url=url,
            description=fmt_tweet_text(text, use_blockquote=False),
            title=f"{name} (@{username})"
        )
        embed.set_footer(
            text=created_at,
            icon_url=author_image_url or self.FOOTER_URL
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
        name: str, author_image_url: Optional[str],
        ref_tweet_data: Optional[TweetData], rt_media_urls: Optional[List[str]]
    ) -> None:
        """Send embed of a retweet to Discord"""
        embeds = []
        embed = Embed(
            color=40473,
            url=url,
            title=f"🔁 {name} (@{username}) retweeted"
        )
        self._add_ref_tweet(
            embed=embed,
            ref_tweet_data=ref_tweet_data,
            text="Retweet deleted by OP"
        )
        embed.set_footer(
            text=created_at,
            icon_url=author_image_url or self.FOOTER_URL
        )
        # Save first embed
        embeds.append(embed)

        # Add media
        if rt_media_urls:
            embeds = self._add_media_embeds(
                url=url, media_urls=rt_media_urls, embeds=embeds
            )

        await self.discord.send(embeds=embeds)

    async def send_quote_tweet_embed(
        self, url: str, text: str, created_at: str, username: str,
        name: str, author_image_url: Optional[str],
        ref_tweet_data: Optional[TweetData],
        media_urls: List[str] = []
    ) -> None:
        """Send embed of a quote tweet to Discord"""
        embeds = []
        embed = Embed(
            color=11468877,
            description=fmt_tweet_text(text, use_blockquote=False),
            url=url,
            title=f"{name} (@{username})"
        )
        self._add_ref_tweet(
            embed=embed,
            ref_tweet_data=ref_tweet_data,
            text="Quoted tweet deleted by OP"
        )
        embed.set_footer(
            text=created_at,
            icon_url=author_image_url or self.FOOTER_URL
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
        name: str, author_image_url: Optional[str],
        ref_tweet_data: Optional[TweetData],
        media_urls: List[str] = []
    ) -> None:
        """Send embed of a reply tweet to Discord"""
        embeds = []
        embed = Embed(
            color=57599,
            description=fmt_tweet_text(text, use_blockquote=False),
            url=url,
            title=f"↪️ {name} (@{username}) replied"
        )
        self._add_ref_tweet(
            embed=embed,
            ref_tweet_data=ref_tweet_data,
            text="Reply deleted by OP"
        )
        embed.set_footer(
            text=created_at,
            icon_url=author_image_url or self.FOOTER_URL
        )
        # Save first embed
        embeds.append(embed)

        # Add media
        embeds = self._add_media_embeds(
            url=url, media_urls=media_urls, embeds=embeds
        )

        await self.discord.send(embeds=embeds)
