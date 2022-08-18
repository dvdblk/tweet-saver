import re


from datetime import datetime
from html import unescape
from zoneinfo import ZoneInfo


def fmt_created_at(d: datetime = datetime.now()) -> str:
    """Create a formatted string from datetime in GMT+2"""
    return d.astimezone(ZoneInfo("Europe/Zurich")).strftime(
        "%H:%M:%S • %d/%m/%Y",
    )

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
