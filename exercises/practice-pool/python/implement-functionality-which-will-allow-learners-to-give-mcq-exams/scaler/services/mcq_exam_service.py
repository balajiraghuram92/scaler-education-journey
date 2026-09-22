from abc import ABC, abstractmethod

from scaler.models import LearnerExam, QuestionResponse


class MCQExamService(ABC):

    @abstractmethod
    def start_exam(
            self,
            learner_id: int,
            exam_id: int
    ) -> LearnerExam:
        pass

    @abstractmethod
    def submit_exam(
            self,
            learner_id: int,
            exam_id: int
    ) -> LearnerExam:
        pass

    @abstractmethod
    def answer_question(
            self,
            exam_id: int,
            learner_id: int,
            question_id: int,
            option_id: int
    ) -> QuestionResponse:
        pass

