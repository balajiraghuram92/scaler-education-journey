from scaler.dtos import ResponseStatus
from scaler.dtos import StartExamReqDto, StartExamResDto
from scaler.dtos import SubmitExamReqDto, SubmitExamResDto
from scaler.dtos import AnswerQuestionReqDto, AnswerQuestionResDto
from scaler.models import LearnerExam, QuestionResponse
from scaler.services import MCQExamService


class MCQExamController:
    mcq_exam_service: MCQExamService

    def __init__(
            self,
            mcq_exam_service: MCQExamService
    ):
        self.mcq_exam_service = mcq_exam_service

    def start_exam(
            self,
            request_dto: StartExamReqDto
    ):

        try:
            response: LearnerExam = self.mcq_exam_service.start_exam(
                exam_id=request_dto.exam_id,
                learner_id=request_dto.learner_id
            )
            response_dto = StartExamResDto(
                learner_exam=response,
                response_status=ResponseStatus.SUCCESS
            )

        except Exception as e:
            response_dto = StartExamResDto(
                learner_exam=None,
                response_status=ResponseStatus.FAILURE
            )

        return response_dto

    def submit_exam(
            self,
            request_dto: SubmitExamReqDto
    ):

        try:
            response: LearnerExam = self.mcq_exam_service.submit_exam(
                exam_id=request_dto.exam_id,
                learner_id=request_dto.learner_id
            )
            response_dto = SubmitExamResDto(
                learner_exam=response,
                response_status=ResponseStatus.SUCCESS
            )

        except Exception as e:
            response_dto = SubmitExamResDto(
                learner_exam=None,
                response_status=ResponseStatus.FAILURE
            )

        return response_dto

    def answer_question(
            self,
            request_dto: AnswerQuestionReqDto
    ):

        try:
            response: QuestionResponse = self.mcq_exam_service.answer_question(
                exam_id=request_dto.exam_id,
                learner_id=request_dto.learner_id,
                question_id=request_dto.question_id,
                option_id=request_dto.option_id
            )
            response_dto = AnswerQuestionResDto(
                question_response=response,
                response_status=ResponseStatus.SUCCESS
            )

        except Exception as e:
            response_dto = AnswerQuestionResDto(
                question_response=None,
                response_status=ResponseStatus.FAILURE
            )

        return response_dto

