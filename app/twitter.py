from typing import List

from tweepy import StreamRule, Tweet
from tweepy.asynchronous import AsyncStreamingClient, AsyncClient

from app import init_logger
from app.discord_manager import DiscordManager

log = init_logger(__name__)


class TweetStreamingClient(AsyncStreamingClient):
    """Manage a filtered stream based on a stream rule string and post new tweets to Discord."""

    def __init__(self, discord: DiscordManager, stream_rule: str, bearer_token, *, return_type=..., wait_on_rate_limit=False, **kwargs):
        self.discord = discord
        self.stream_rule_str = stream_rule
        self.client = AsyncClient(bearer_token=bearer_token)
        super().__init__(bearer_token, return_type=return_type, wait_on_rate_limit=False, **kwargs)

    async def prepare_rules(self, remove_previous_rules: bool = True):
        """
        Adds the rules from config.json to a filtered stream.
        Optionally also removes the previous (currently active) rules.

        Args:
            remove_previous_rules (bool): remove currently active rules
                                            before adding new ones
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

    async def on_tweet(self, tweet: Tweet):
        # Get tweet URL
        tweet_data = await self.client.get_tweet(
            id=tweet.id,
            tweet_fields=["entities", "attachments", "referenced_tweets", "created_at", "author_id"],
            expansions=["author_id"],
        )
        log.info(tweet_data)

        # Send tweet to Discord
        tweet_url = f"https://twitter.com/twitter/statuses/{tweet.id}"
        log.info(f"Sending new tweet: {tweet_url}")
        await self.discord.send_new_tweet(tweet_url=tweet_url)

    async def start_filtered_stream(self):
        """Apply rules and start listening for new tweets"""
        await self.prepare_rules()
        log.info("Starting filtered stream...")
        await self.filter()
