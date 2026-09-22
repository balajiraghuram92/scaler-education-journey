from dataclasses import dataclass, field

from .response_status import ResponseStatus


@dataclass
class UnregisterUserNotifyResDto:
    response_status: ResponseStatus = field(default=None)
