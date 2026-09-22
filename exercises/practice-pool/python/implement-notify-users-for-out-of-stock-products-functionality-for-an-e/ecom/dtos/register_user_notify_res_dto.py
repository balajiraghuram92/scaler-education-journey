from dataclasses import dataclass, field

from .response_status import ResponseStatus


@dataclass
class RegisterUserNotifyResDto:
    notification_id: int = field(default=None)
    response_status: ResponseStatus = field(default=None)
