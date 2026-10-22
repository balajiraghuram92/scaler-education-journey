from ecom.dtos import (
    RegisterUserNotifyReqDto,
    RegisterUserNotifyResDto,
    ResponseStatus,
    UnregisterUserNotifyReqDto,
    UnregisterUserNotifyResDto,
)
from ecom.services.notification_service import NotificationService


class NotificationController:
    def __init__(self, notification_service: NotificationService) -> None:
        self.notification_service = notification_service

    def register_user(self, request_dto: RegisterUserNotifyReqDto) -> RegisterUserNotifyResDto:
        try:
            notification = self.notification_service.register_user(request_dto.user_id, request_dto.product_id)
            return RegisterUserNotifyResDto(response_status=ResponseStatus.SUCCESS, notification_id=notification.id)
        except Exception:
            return RegisterUserNotifyResDto(response_status=ResponseStatus.FAILURE)

    def unregister_user(self, request_dto: UnregisterUserNotifyReqDto) -> UnregisterUserNotifyResDto:
        try:
            self.notification_service.unregister_user(request_dto.user_id, request_dto.product_id)
            return UnregisterUserNotifyResDto(response_status=ResponseStatus.SUCCESS)
        except Exception:
            return UnregisterUserNotifyResDto(response_status=ResponseStatus.FAILURE)
