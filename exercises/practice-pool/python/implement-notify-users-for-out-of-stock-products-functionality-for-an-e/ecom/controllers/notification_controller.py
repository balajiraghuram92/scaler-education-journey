from ecom.services import NotificationService
from ecom.dtos import RegisterUserNotifyReqDto, RegisterUserNotifyResDto, ResponseStatus
from ecom.dtos import UnregisterUserNotifyReqDto, UnregisterUserNotifyResDto
from logging import getLogger, DEBUG
import traceback


class NotificationController:
    notification_service: NotificationService

    def __init__(
            self,
            notification_service: NotificationService
    ):
        self.notification_service = notification_service
        self.logger = getLogger(__name__)
        self.logger.setLevel(DEBUG)

    def register_user(
            self,
            request_dto: RegisterUserNotifyReqDto
    ):
        try:
            notification = self.notification_service.register_user(
                request_dto.user_id,
                request_dto.product_id,
            )

            response = RegisterUserNotifyResDto(
                response_status=ResponseStatus.SUCCESS,
                notification_id=notification.pk
            )
        except Exception as e:
            self.logger.debug(traceback.format_exc())
            response = RegisterUserNotifyResDto(
                response_status=ResponseStatus.FAILURE
            )

        return response



    def unregister_user(
            self,
            request_dto: RegisterUserNotifyReqDto
    ):
        try:
            self.notification_service.unregister_user(
                request_dto.user_id,
                request_dto.product_id,
            )

            response = RegisterUserNotifyResDto(
                response_status=ResponseStatus.SUCCESS,
            )
        except Exception as e:
            self.logger.debug(traceback.format_exc())
            response = RegisterUserNotifyResDto(
                response_status=ResponseStatus.FAILURE
            )

        return response
