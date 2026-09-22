from food_delivery.dtos import BuildBatchedTaskRouteResponseDto, BuildBatchedTaskRouteRequestDto
from food_delivery.dtos import ResponseStatus
from logging import getLogger, DEBUG
import traceback

from food_delivery.services import BatchedTaskService


class BatchedTaskController:
    batched_task_service: BatchedTaskService

    def __init__(
            self,
            batched_task_service: BatchedTaskService
    ):
        self.batched_task_service = batched_task_service
        self.logger = getLogger(__name__)
        self.logger.setLevel(DEBUG)

    def build_route(
            self,
            request_dto: BuildBatchedTaskRouteRequestDto
    ):
        try:
            locations = self.batched_task_service.build_route(
                batched_task_id=request_dto.batched_task_id
            )

            response = BuildBatchedTaskRouteResponseDto(
                response_status=ResponseStatus.SUCCESS,
                route_to_be_taken=locations
            )

        except Exception as e:
            self.logger.debug(traceback.format_exc())
            response = BuildBatchedTaskRouteResponseDto(
                response_status=ResponseStatus.FAILURE
            )

        return response
