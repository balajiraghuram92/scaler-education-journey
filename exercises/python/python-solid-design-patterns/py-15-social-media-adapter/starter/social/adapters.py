from abc import ABC, abstractmethod
from typing import List

from .model import FacebookPost, SocialMediaPost, TwitterTweet
from .services import FacebookApi, TwitterApi


class SocialMediaAdapter(ABC):
    """Target interface: two abstract methods.

    - get_posts(user_id: int, timestamp: int) -> List[SocialMediaPost]
    - post(user_id: int, message: str) -> None
    """


class TwitterAdapter(SocialMediaAdapter):
    """Wraps TwitterApi; keep the client in ``self.twitter_api`` (created in __init__).

    Tweets have no timestamp, so the resulting SocialMediaPost.timestamp is None.
    ``TwitterTweet.tweet`` becomes ``SocialMediaPost.text``.
    """

    def __init__(self):
        raise NotImplementedError("Create self.twitter_api")


class FacebookAdapter(SocialMediaAdapter):
    """Wraps FacebookApi; keep the client in ``self.facebook_api`` (created in __init__).

    ``FacebookPost.status`` becomes ``SocialMediaPost.text``; the timestamp is copied across.
    """

    def __init__(self):
        raise NotImplementedError("Create self.facebook_api")
