from tweepy import StreamRule, Tweet
from tweepy.asynchronous import AsyncClient, AsyncStreamingClient

from app import init_logger
from app.discord_manager import DiscordManager
from app.twitter.model import TweetData, TweetType

log = init_logger(__name__)


class TweetStreamingClient(AsyncStreamingClient):
    """Twitter API v2 streaming client.

    Manage a filtered stream based on a stream rule string and post new tweets to Discord.
    """
    # Args passed to filter and GET /2/tweets/:id requests
    TWEET_DATA_ARGS=dict(
        tweet_fields=["entities", "attachments", "referenced_tweets", "created_at"],
        media_fields=["preview_image_url", "url"],
        user_fields=["username", "name", "profile_image_url"],
        expansions=["attachments.media_keys", "author_id"]
    )

    def __init__(self, discord: DiscordManager, stream_rule: str, bearer_token, *, return_type=..., wait_on_rate_limit=False, **kwargs):
        self.discord = discord
        self.stream_rule_str = stream_rule
        self.client: AsyncClient = AsyncClient(bearer_token=bearer_token)
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
        previous_rules = resp.data or []

        # Remove previous rules if needed
        if remove_previous_rules:
            # Don't remove the rule we're about to add
            prev_rules_to_delete = list(filter(lambda r: r.value != stream_rule.value, previous_rules))
            previous_rule_ids = list(map(lambda x: x.id, prev_rules_to_delete))
            if previous_rule_ids:
                log.info(f"Deleting rule(s): {list(map(lambda r: r.value, prev_rules_to_delete))}")
                # Remove irrelevant rules
                await self.delete_rules(previous_rule_ids)

        # Only add the rule if it's not already added
        if not stream_rule.value in list(map(lambda r: r.value, previous_rules)):
            log.info(f'Adding stream rule: "{self.stream_rule_str}"')
            await self.add_rules(StreamRule(self.stream_rule_str))

        log.info(f'Current filtered stream rule: "{self.stream_rule_str}"')

    async def on_response(self, response):
        """Get additional tweet data and send Embed to Discord.

        Note:   gets called by `AsyncStreamingClient` when a new tweet matches the StreamRule. This
                method is used instead of `on_tweet` because response contains additional request data args
                unlike with `on_tweet`.
        """
        if response.data is None:
            # Skip sending when data is None
            log.warning(f"Response data is None for response: {response}")
            return
        # Get TweetData
        tweet_data = TweetData.parse_tweet_data(response)
        # Send an embed based on tweet type
        if ref_tweet_id := tweet_data.reference_id:
            # If the tweet data contains a reference to another tweet,
            # get referenced tweet data
            ref_tweet_data = None
            if ref_tweet := await self.client.get_tweet(
                id=ref_tweet_id,
                **self.TWEET_DATA_ARGS
            ):
                # Reference tweet not deleted yet
                ref_tweet_data = TweetData.parse_tweet_data(ref_tweet)
            if tweet_data.tweet_type == TweetType.RETWEET:
                # Retweet
                log.info(f"New retweet: {tweet_data.url}")
                await self.discord.send_retweet_embed(
                    url=tweet_data.url,
                    created_at=tweet_data.created_at,
                    username=tweet_data.username,
                    name=tweet_data.name,
                    author_image_url=tweet_data.profile_image_url,
                    ref_tweet_data=ref_tweet_data,
                    rt_media_urls=ref_tweet_data.media_urls
                )
            elif tweet_data.tweet_type == TweetType.QUOTE:
                # Quote tweet
                log.info(f"New quote tweet: {tweet_data.url}")
                await self.discord.send_quote_tweet_embed(
                    url=tweet_data.url,
                    text=tweet_data.text,
                    created_at=tweet_data.created_at,
                    username=tweet_data.username,
                    name=tweet_data.name,
                    author_image_url=tweet_data.profile_image_url,
                    media_urls=tweet_data.media_urls,
                    ref_tweet_data=ref_tweet_data
                )
            elif tweet_data.tweet_type == TweetType.REPLY:
                # Reply tweet
                log.info(f"New reply tweet: {tweet_data.url}")
                await self.discord.send_reply_tweet_embed(
                    url=tweet_data.url,
                    text=tweet_data.text,
                    created_at=tweet_data.created_at,
                    username=tweet_data.username,
                    name=tweet_data.name,
                    author_image_url=tweet_data.profile_image_url,
                    ref_tweet_data=ref_tweet_data,
                    media_urls=tweet_data.media_urls,
                )
        else:
            # If the tweet data doesn't contain a reference to another tweet
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
            elif tweet_data.tweet_type == TweetType.UNKNOWN:
                # Unknown tweet
                log.warning(f"Unknown tweet type: {tweet_data.url}")
            else:
                log.warning(f"Tweet without reference is not a TweetType.NORMAL tweet! {tweet_data.url}")

    async def on_connection_error(self):
        """Called on stream timeout by `AsyncStream`"""
        await super().on_connection_error()
        # Disconnect from the stream
        log.info("Disconnecting")
        await self.disconnect()
        log.info("Disconnected")
        # Reconnect
        await self.start_filtered_stream()

    async def start_filtered_stream(self):
        """Apply rules and start listening for new tweets"""
        await self.prepare_rules()
        log.info("Starting filtered stream.")
        await self.filter(**self.TWEET_DATA_ARGS)
