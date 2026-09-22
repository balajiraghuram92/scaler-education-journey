from typing import List

from scaler.models import BatchLearner
from scaler.services import BatchService
from scaler.dtos import AddLearnerToBatchReqDto, AddLearnerToBatchResDto
from scaler.dtos import RemoveLearnerFromBatchReqDto, RemoveLearnerFromBatchResDto
from scaler.dtos import ResponseStatus


class BatchController:
    batch_service: BatchService

    def __init__(
            self,
            batch_service: BatchService
    ):
        self.batch_service = batch_service

    def add_learner_to_batch(
            self,
            request_dto: AddLearnerToBatchReqDto
    ):

        try:
            response: BatchLearner = self.batch_service.add_learner_to_batch(
                learner_id=request_dto.learner_id,
                batch_id=request_dto.batch_id,
                admin_id=request_dto.admin_id
            )

            response_dto = AddLearnerToBatchResDto(
                batch_learner=response,
                response_status=ResponseStatus.SUCCESS
            )

        except Exception as e:
            response_dto = AddLearnerToBatchResDto(
                batch_learner=None,
                response_status=ResponseStatus.FAILURE
            )

        return response_dto

    def remove_learner_from_batch(
            self,
            request_dto: RemoveLearnerFromBatchReqDto
    ):

        try:
            response: BatchLearner = self.batch_service.remove_learner_from_batch(
                learner_id=request_dto.learner_id,
                batch_id=request_dto.batch_id,
                admin_id=request_dto.admin_id
            )

            response_dto = RemoveLearnerFromBatchResDto(
                batch_learner=response,
                response_status=ResponseStatus.SUCCESS
            )

        except Exception as e:
            response_dto = RemoveLearnerFromBatchResDto(
                batch_learner=None,
                response_status=ResponseStatus.FAILURE
            )

        return response_dto
