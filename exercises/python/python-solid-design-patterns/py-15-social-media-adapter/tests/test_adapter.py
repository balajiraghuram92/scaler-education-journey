import dataclasses
import inspect

import pytest

from social.adapters import FacebookAdapter, SocialMediaAdapter, TwitterAdapter
from social.model import FacebookPost, SocialMediaPost, TwitterTweet
from social.services import FacebookApi, TwitterApi


class SpyTwitter:
    def __init__(self, tweets=()):
        self.tweets = list(tweets)
        self.fetch_calls = []
        self.sent = []

    def get_tweets(self, user_id):
        self.fetch_calls.append(user_id)
        return list(self.tweets)

    def tweet(self, user_id, text):
        self.sent.append((user_id, text))


class SpyFacebook:
    def __init__(self, posts=()):
        self.posts = list(posts)
        self.fetch_calls = []
        self.sent = []

    def fetch_facebook_posts(self, user_id, timestamp):
        self.fetch_calls.append((user_id, timestamp))
        return list(self.posts)

    def post_facebook_status(self, user_id, status):
        self.sent.append((user_id, status))


def twitter(spy):
    adapter = TwitterAdapter()
    adapter.twitter_api = spy
    return adapter


def facebook(spy):
    adapter = FacebookAdapter()
    adapter.facebook_api = spy
    return adapter


def test_interface_is_abstract_with_get_posts_and_post():
    assert inspect.isabstract(SocialMediaAdapter), "SocialMediaAdapter must be an ABC with abstract methods"
    assert SocialMediaAdapter.__abstractmethods__ == {"get_posts", "post"}, (
        f"expected abstract get_posts and post, found {sorted(SocialMediaAdapter.__abstractmethods__)}"
    )
    with pytest.raises(TypeError):
        SocialMediaAdapter()


def test_adapters_wrap_platform_clients_by_composition():
    t, f = TwitterAdapter(), FacebookAdapter()
    assert isinstance(t, SocialMediaAdapter) and isinstance(f, SocialMediaAdapter)
    assert isinstance(t.twitter_api, TwitterApi), "twitter_api must hold a TwitterApi"
    assert isinstance(f.facebook_api, FacebookApi), "facebook_api must hold a FacebookApi"
    assert not isinstance(t, TwitterApi) and not isinstance(f, FacebookApi), "do not subclass the platform clients"


def test_twitter_maps_tweets_with_no_timestamp():
    spy = SpyTwitter([TwitterTweet("1", "Tweet 1", 123), TwitterTweet("2", "Tweet 2", 456)])
    posts = twitter(spy).get_posts(123, 999)
    assert spy.fetch_calls == [123], "Twitter's API takes only the user id"
    assert posts == [
        SocialMediaPost("1", "Tweet 1", 123, None),
        SocialMediaPost("2", "Tweet 2", 456, None),
    ], f"tweets must map to SocialMediaPost with timestamp None, got {posts}"
    assert all(type(p) is SocialMediaPost for p in posts), "return SocialMediaPost instances"


def test_facebook_maps_status_to_text_and_copies_timestamp():
    spy = SpyFacebook([FacebookPost("1", "Post 1", 123, 123456), FacebookPost("2", "Post 2", 456, 789012)])
    posts = facebook(spy).get_posts(123, 50)
    assert spy.fetch_calls == [(123, 50)], "the user id and timestamp must reach Facebook"
    assert posts == [
        SocialMediaPost("1", "Post 1", 123, 123456),
        SocialMediaPost("2", "Post 2", 456, 789012),
    ], f"Facebook posts must map status->text and keep the timestamp, got {posts}"


def test_empty_feed_returns_empty_list():
    assert twitter(SpyTwitter()).get_posts(1, 0) == []
    assert facebook(SpyFacebook()).get_posts(1, 0) == []


def test_post_delegates_to_each_platform():
    t, f = SpyTwitter(), SpyFacebook()
    twitter(t).post(7, "Hello Twitter!")
    facebook(f).post(8, "Hello Facebook!")
    assert t.sent == [(7, "Hello Twitter!")], "TwitterAdapter.post must call tweet(user_id, text)"
    assert f.sent == [(8, "Hello Facebook!")], "FacebookAdapter.post must call post_facebook_status(user_id, status)"


def test_common_post_type_keeps_its_four_fields():
    names = [f.name for f in dataclasses.fields(SocialMediaPost)]
    assert names == ["id", "text", "user_id", "timestamp"], f"SocialMediaPost fields changed: {names}"


def test_aggregator_merges_platforms_through_the_interface():
    adapters = [
        twitter(SpyTwitter([TwitterTweet("t1", "hi", 1)])),
        facebook(SpyFacebook([FacebookPost("f1", "yo", 1, 10)])),
    ]
    merged = [p for a in adapters for p in a.get_posts(1, 0)]
    assert [(p.id, p.text) for p in merged] == [("t1", "hi"), ("f1", "yo")], (
        "client code should treat both platforms uniformly through SocialMediaAdapter"
    )
