from typing import Any
from zoneinfo import ZoneInfo

from tweepy.asynchronous import AsyncClient
from tweepy.client import Response

from app.twitter.model import TweetData, TweetType


class TwitterClient(AsyncClient):
    """Twitter API v2 client."""

    async def get_tweet_data(self, id: Any) -> TweetData:
        """get_tweet with predefined query params, returns `TweetData`"""
        # Get tweet data
        tweet_data = await self.get_tweet(
            id=id,
            tweet_fields=["entities", "attachments", "referenced_tweets", "created_at"],
            media_fields=["preview_image_url", "url"],
            user_fields=["username", "name"],
            expansions=["attachments.media_keys", "author_id"],
        )

        # Get additional tweet data
        tweet_username = "unk"
        tweet_name = "unk"
        if users := tweet_data.includes.get("users"):
            tweet_username = users[0].username
            tweet_name = users[0].name
            tweet_url = f"https://twitter.com/{tweet_username}/status/{id}"
        else:
            tweet_url = f"https://twitter.com/twitter/statuses/{id}"
        tweet_created_at = tweet_data.data.get(
            "created_at", "1337-01-01 13:37:00+00:00"
        ).astimezone(ZoneInfo("Europe/Zurich")).strftime(
            "%H:%M:%S • %d.%m.%Y",
        )
        tweet_text = tweet_data.data["text"]

        # Get media URLs from tweet data
        media_urls = []
        if media_list := tweet_data.includes.get("media"):
            for media in media_list:
                if url := media.get("url"):
                    media_urls.append(url)

        tweet_type, reference_id = TweetType.NORMAL, None
        if referenced_tweets := tweet_data.data.get("referenced_tweets"):
            ref_tweet = referenced_tweets[0]
            tweet_type = TweetType(ref_tweet.type)
            reference_id = ref_tweet.id

        return TweetData(
            id=id,
            text=tweet_text,
            username=tweet_username,
            name=tweet_name,
            url=tweet_url,
            created_at=tweet_created_at,
            tweet_type=tweet_type,
            reference_id=reference_id,
            media_urls=media_urls
        )
