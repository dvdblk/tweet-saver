from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class TweetType(str, Enum):
    NORMAL = "normal"
    RETWEET = "retweeted"
    QUOTE = "quoted"


@dataclass
class TweetData:
    id: str
    text: str
    username: str
    name: str
    url: str
    created_at: str
    tweet_type: TweetType
    reference_id: Optional[str]
    media_urls: List[str]
