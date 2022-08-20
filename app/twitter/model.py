from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional

from tweepy import Response

from app.twitter import fmt_created_at


class TweetType(str, Enum):
    """The type of a tweet"""
    NORMAL = "normal"
    RETWEET = "retweeted"
    QUOTE = "quoted"
    REPLY = "replied_to"
    UNKNOWN = "unk"


@dataclass
class TweetData:
    """Data relevant for creating Discord embeds from tweets"""
    # unique ID of the tweet
    id: str
    # tweet text
    text: str
    # author's username
    username: str
    # author's name
    name: str
    # author's profile image URL
    profile_image_url: Optional[str]
    # tweet URL
    url: str
    # Date of tweet creation in ISO format
    created_at: str
    # The type of the tweet
    tweet_type: TweetType
    # Optional ID of a tweet this tweet refers to
    # (not null if tweet type is not TweetType.NORMAL)
    reference_id: Optional[str]
    # list of images attached to a tweet
    media_urls: List[str]

    @staticmethod
    def parse_tweet_data(tweet: Response) -> TweetData:
        """Parse the response of GET /2/tweets/:id and return `TweetData`"""
        tweet_username = "unk"
        tweet_name = "unk"
        if users := tweet.includes.get("users"):
            tweet_username = users[0].username
            tweet_name = users[0].name
            author_profile_image_url = users[0].profile_image_url
            tweet_url = f"https://twitter.com/{tweet_username}/status/{tweet.data.id}"
        else:
            tweet_url = f"https://twitter.com/twitter/statuses/{tweet.data.id}"
        tweet_created_at = fmt_created_at(
            tweet.data.get(
                "created_at", "1337-01-01 13:37:00+00:00"
            )
        )
        tweet_text = tweet.data["text"]

        # Get media URLs from tweet data
        media_urls = []
        if media_list := tweet.includes.get("media"):
            for media in media_list:
                if url := media.get("url"):
                    media_urls.append(url)

        tweet_type, reference_id = TweetType.NORMAL, None
        try:
            if referenced_tweets := tweet.data.get("referenced_tweets"):
                ref_tweet = referenced_tweets[0]
                tweet_type = TweetType(ref_tweet.type)
                reference_id = ref_tweet.id
            else:
                tweet_type = TweetType.NORMAL
        except ValueError:
            tweet_type = TweetType.UNKNOWN

        return TweetData(
            id=tweet.data.id,
            text=tweet_text,
            username=tweet_username,
            name=tweet_name,
            profile_image_url=author_profile_image_url,
            url=tweet_url,
            created_at=tweet_created_at,
            tweet_type=tweet_type,
            reference_id=reference_id,
            media_urls=media_urls
        )
