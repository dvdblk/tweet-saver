#!/bin/sh

docker build . -t tweet_saver && \
docker run --env-file .env tweet_saver
