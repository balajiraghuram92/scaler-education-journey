from typing import Optional

from .response_status import ResponseStatus
from dataclasses import dataclass
from scaler.models import LearnerExam, QuestionResponse


@dataclass
class StartExamReqDto:
    learner_id: int
    exam_id: int


@dataclass
class SubmitExamReqDto:
    learner_id: int
    exam_id: int


@dataclass
class AnswerQuestionReqDto:
    learner_id: int
    exam_id: int
    question_id: int
    option_id: int


@dataclass
class StartExamResDto:
    learner_exam: Optional[LearnerExam]
    response_status: ResponseStatus


@dataclass
class SubmitExamResDto:
    learner_exam: Optional[LearnerExam]
    response_status: ResponseStatus


@dataclass
class AnswerQuestionResDto:
    question_response: Optional[QuestionResponse]
    response_status: ResponseStatus






