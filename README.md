# Tweet Saver

<p align="center">
  <a href="https://hub.docker.com/repository/docker/dvdblk/tweet-saver" alt="Docker Version">
    <img src="https://img.shields.io/docker/v/dvdblk/tweet-saver?label=version&sort=semver"/>
  </a>
  <a href="https://hub.docker.com/repository/docker/dvdblk/tweet-saver" alt="Docker Pulls">
    <img src="https://img.shields.io/docker/pulls/dvdblk/tweet-saver"/>
  </a>
  <a href="https://hub.docker.com/repository/docker/dvdblk/tweet-saver" alt="Docker Image size">
    <img src="https://img.shields.io/docker/image-size/dvdblk/tweet-saver?sort=date"/>
  </a>
  <a href="LICENSE" alt="GitHub License">
    <img src="https://img.shields.io/github/license/dvdblk/tweet-saver?label=license"/>
  </a>
</p>

This app allows you to filter the real-time stream of all public tweets and send the matching ones to Discord. Just create your own [Stream Rule](https://developer.twitter.com/en/docs/twitter-api/tweets/filtered-stream/integrate/build-a-rule) and start the app.


## Run the app
Easiest way to run this is via Docker:

```
$ docker run --env-file <your-env-file> dvdblk/tweet-saver:latest
```

### ENV variables
To successfully run the app you need to pass these environment variables to the docker container:

| ENV_VAR                      | Description                                  |
|------------------------------|----------------------------------------------|
| DISCORD_WEBHOOK_URL          | Tweets will be sent to this Discord channel. |
| TWITTER_BEARER_TOKEN         | Twitter API OAuth 2.0 Bearer Token / Access Token |
| TWITTER_FILTERED_STREAM_RULE | The [Stream Rule](https://developer.twitter.com/en/docs/twitter-api/tweets/filtered-stream/integrate/build-a-rule) for filtering tweets. (e.g. `from:elonmusk`) |

You can pass these to `docker run` in an `.env` file with `--env-file <your-env-file>` or manually with `-e DISCORD_WEBHOOK_URL=...`.

## Custom Discord Embeds
The app sends custom Discord Embeds for three types of tweets (regular, retweet and quote). Also supports images.

<p align="center" width="100%">
    <img width="30%" src="etc/embed_preview.png">
</p>
