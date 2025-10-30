# -*- coding: utf-8 -*-
import os
import tweepy

from dotenv import load_dotenv
load_dotenv()

X_CONSUMER_KEY = os.getenv("X_CONSUMER_KEY")
X_CONSUMER_SECRET = os.getenv("X_CONSUMER_SECRET")
X_ACCESS_TOKEN = os.getenv("X_ACCESS_TOKEN")
X_ACCESS_TOKEN_SECRET = os.getenv("X_ACCESS_TOKEN_SECRET")

def _client():
    # Tweepy v4: Client + OAuth 1.0a user context
    client = tweepy.Client(
        consumer_key=X_CONSUMER_KEY,
        consumer_secret=X_CONSUMER_SECRET,
        access_token=X_ACCESS_TOKEN,
        access_token_secret=X_ACCESS_TOKEN_SECRET
    )
    return client

def post_to_x(text: str):
    client = _client()
    # create_tweet — X API v2
    resp = client.create_tweet(text=text)
    return resp.data
