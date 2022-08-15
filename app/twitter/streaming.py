from tweepy import StreamRule, Tweet
from tweepy.asynchronous import AsyncStreamingClient

from app import init_logger
from app.discord_manager import DiscordManager
from app.twitter.client import TwitterClient
from app.twitter.model import TweetType

log = init_logger(__name__)


class TweetStreamingClient(AsyncStreamingClient):
    """Twitter API v2 streaming client.

    Manage a filtered stream based on a stream rule string and post new tweets to Discord.
    """

    def __init__(self, discord: DiscordManager, stream_rule: str, bearer_token, *, return_type=..., wait_on_rate_limit=False, **kwargs):
        self.discord = discord
        self.stream_rule_str = stream_rule
        self.client: TwitterClient = TwitterClient(bearer_token=bearer_token)
        super().__init__(bearer_token, return_type=return_type, wait_on_rate_limit=False, **kwargs)

    async def prepare_rules(self, remove_previous_rules: bool = True):
        """
        Add the rule from TWITTER_FILTERED_STREAM_RULE to a filtered stream.
        Optionally also removes the previous (currently active) rules.

        Args:
            remove_previous_rules (bool): remove currently active rules
                                            before adding the new one
        """
        # Create the StreamRule
        stream_rule = StreamRule(self.stream_rule_str)

        # Get previous rules
        resp = await self.get_rules()
        previous_rules = resp.data

        # Remove previous rules if needed
        if remove_previous_rules:
            # Don't remove the rule we're about to add
            prev_rules_to_delete = filter(lambda r: r.value != stream_rule.value, previous_rules)
            previous_rule_ids = list(map(lambda x: x.id, prev_rules_to_delete))

            if previous_rule_ids:
                log.info(f"Deleting rule(s) with ids: {previous_rule_ids}")
                # Remove irrelevant rules
                await self.delete_rules(previous_rule_ids)

        # Only add the rule if it's not already added
        if not stream_rule.value in list(map(lambda r: r.value, previous_rules)):
            log.info(f'Adding stream rule: "{self.stream_rule_str}"')
            await self.add_rules(StreamRule(self.stream_rule_str))

        log.info(f'Current filtered stream rule: "{self.stream_rule_str}"')

    async def on_tweet(self, tweet: Tweet) -> None:
        """Get additional tweet data and send Embed to Discord.

        Note: gets called by `AsyncStreamingClient` when a new tweet matches the StreamRule
        """
        # Get TweetData
        tweet_data = await self.client.get_tweet_data(id=tweet.id)

        # Send an embed based on tweet type
        if tweet_data.tweet_type == TweetType.NORMAL:
            # Regular Tweet
            log.info(f"New tweet: {tweet_data.url}")
            await self.discord.send_tweet_embed(
                url=tweet_data.url,
                text=tweet_data.text,
                created_at=tweet_data.created_at,
                username=tweet_data.username,
                name=tweet_data.name,
                author_image_url=tweet_data.profile_image_url,
                media_urls=tweet_data.media_urls
            )
        elif tweet_data.tweet_type == TweetType.RETWEET:
            # Retweet
            ref_tweet_data = await self.client.get_tweet_data(
                id=tweet_data.reference_id
            )
            log.info(f"New retweet: {tweet_data.url}")
            await self.discord.send_retweet_embed(
                url=tweet_data.url,
                created_at=tweet_data.created_at,
                username=tweet_data.username,
                name=tweet_data.name,
                author_image_url=tweet_data.profile_image_url,
                rt_name=ref_tweet_data.name,
                rt_username=ref_tweet_data.username,
                rt_text=ref_tweet_data.text,
                rt_media_urls=ref_tweet_data.media_urls
            )
        elif tweet_data.tweet_type == TweetType.QUOTE:
            # Quote tweet
            ref_tweet_data = await self.client.get_tweet_data(
                id=tweet_data.reference_id
            )
            log.info(f"New quote tweet: {tweet_data.url}")
            await self.discord.send_quote_tweet_embed(
                url=tweet_data.url,
                text=tweet_data.text,
                created_at=tweet_data.created_at,
                username=tweet_data.username,
                name=tweet_data.name,
                author_image_url=tweet_data.profile_image_url,
                media_urls=tweet_data.media_urls,
                rt_name=ref_tweet_data.name,
                rt_username=ref_tweet_data.username,
                rt_text=ref_tweet_data.text
            )
        elif tweet_data.tweet_type == TweetType.REPLY:
            # Reply tweet
            ref_tweet_data = await self.client.get_tweet_data(
                id=tweet_data.reference_id
            )
            log.info(f"New reply tweet: {tweet_data.url}")
            await self.discord.send_reply_tweet_embed(
                url=tweet_data.url,
                text=tweet_data.text,
                created_at=tweet_data.created_at,
                username=tweet_data.username,
                name=tweet_data.name,
                author_image_url=tweet_data.profile_image_url,
                media_urls=tweet_data.media_urls,
                rt_name=ref_tweet_data.name,
                rt_username=ref_tweet_data.username,
                rt_text=ref_tweet_data.text
            )
        elif tweet_data.tweet_type == TweetType.UNKNOWN:
            # Unknown tweet
            log.warning(f"Unknown tweet type: {tweet_data.url}")


    async def start_filtered_stream(self):
        """Apply rules and start listening for new tweets"""
        await self.prepare_rules()
        log.info("Starting filtered stream.")
        await self.filter()
