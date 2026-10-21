from abc import ABC

from .api import Api
from .utils import ApiUtils


class BaseApiDecorator(ABC):
    """Base decorator: it IS an Api and it HAS an Api.

    - inherit from Api (and ABC)
    - __init__(api) stores the wrapped API in an instance attribute named ``api``
    - execute_request(data) delegates to ``self.api.execute_request(data)`` and returns its result
    """


class LoggingDecorator(BaseApiDecorator):
    """Call ApiUtils.log_request(data), then delegate to the wrapped API.

    Pass the API to the parent constructor with ``super().__init__(api)`` and return
    the wrapped call's result unchanged.
    """


class RateLimitDecorator(BaseApiDecorator):
    """Call ApiUtils.apply_rate_limit(data) (it takes the request data), then delegate.

    Pass the API to the parent constructor with ``super().__init__(api)`` and return
    the wrapped call's result unchanged.
    """
