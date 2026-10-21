from dataclasses import dataclass


@dataclass
class SocialMediaPost:
    id: str
    text: str
    user_id: int
    timestamp: int


@dataclass
class FacebookPost:
    id: str
    status: str
    user_id: int
    timestamp: int


@dataclass
class TwitterTweet:
    id: str
    tweet: str
    user_id: int
