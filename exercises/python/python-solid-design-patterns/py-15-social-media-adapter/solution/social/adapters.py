from abc import ABC, abstractmethod
from typing import List

from .model import FacebookPost, SocialMediaPost, TwitterTweet
from .services import FacebookApi, TwitterApi


class SocialMediaAdapter(ABC):
    @abstractmethod
    def get_posts(self, user_id: int, timestamp: int) -> List[SocialMediaPost]:
        pass

    @abstractmethod
    def post(self, user_id: int, message: str) -> None:
        pass


class TwitterAdapter(SocialMediaAdapter):
    def __init__(self):
        self.twitter_api = TwitterApi()

    def get_posts(self, user_id: int, timestamp: int) -> List[SocialMediaPost]:
        tweets = self.twitter_api.get_tweets(user_id)
        return [self._to_social_media_post(tweet) for tweet in tweets]

    def post(self, user_id: int, message: str) -> None:
        self.twitter_api.tweet(user_id, message)

    @staticmethod
    def _to_social_media_post(tweet: TwitterTweet) -> SocialMediaPost:
        return SocialMediaPost(tweet.id, tweet.tweet, tweet.user_id, None)


class FacebookAdapter(SocialMediaAdapter):
    def __init__(self):
        self.facebook_api = FacebookApi()

    def get_posts(self, user_id: int, timestamp: int) -> List[SocialMediaPost]:
        posts = self.facebook_api.fetch_facebook_posts(user_id, timestamp)
        return [self._to_social_media_post(post) for post in posts]

    def post(self, user_id: int, message: str) -> None:
        self.facebook_api.post_facebook_status(user_id, message)

    @staticmethod
    def _to_social_media_post(post: FacebookPost) -> SocialMediaPost:
        return SocialMediaPost(post.id, post.status, post.user_id, post.timestamp)
