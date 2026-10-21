from typing import List
from .model import FacebookPost, TwitterTweet


# External Facebook API
class FacebookApi:
    def fetch_facebook_posts(
        self, user_id: int, timestamp: int
    ) -> List["FacebookPost"]:
        # Implementation to fetch Facebook posts
        return [FacebookPost("1", "Hello World", 1, 123456789)]

    def post_facebook_status(self, user_id: int, status: str) -> None:
        # Implementation to post a status on Facebook
        pass

# External Twitter API
class TwitterApi:
    def get_tweets(self, user_id: int) -> List["TwitterTweet"]:
        # Implementation to fetch Twitter tweets
        return [TwitterTweet("1", "Hello World", 1)]

    def tweet(self, user_id: int, text: str) -> None:
        # Implementation to send a tweet on Twitter
        pass