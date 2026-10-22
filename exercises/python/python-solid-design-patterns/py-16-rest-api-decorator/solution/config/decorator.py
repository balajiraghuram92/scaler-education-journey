from abc import ABC

from .api import Api
from .utils import ApiUtils


class BaseApiDecorator(Api, ABC):
    def __init__(self, api: Api):
        self.api = api

    def execute_request(self, data):
        return self.api.execute_request(data)


class LoggingDecorator(BaseApiDecorator):
    def __init__(self, api: Api):
        super().__init__(api)

    def execute_request(self, data):
        ApiUtils.log_request(data)
        return super().execute_request(data)


class RateLimitDecorator(BaseApiDecorator):
    def __init__(self, api: Api):
        super().__init__(api)

    def execute_request(self, data):
        # ApiUtils.apply_rate_limit takes the request data; the course reference called it
        # with no argument, which raises TypeError against the real helper.
        ApiUtils.apply_rate_limit(data)
        return super().execute_request(data)
