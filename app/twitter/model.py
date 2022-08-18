from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


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
