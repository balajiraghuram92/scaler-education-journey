from .mcq_exam_service import MCQExamService
from scaler.exceptions import NotFoundError
from scaler.models import LearnerExam, Learner, Exam, QuestionResponse, ExamStatus
from django.utils import timezone


class MCQExamServiceImpl(MCQExamService):

    def start_exam(
            self,
            learner_id: int,
            exam_id: int
    ) -> LearnerExam:
        learner = Learner.objects.filter(pk=learner_id).first()
        if not learner:
            raise NotFoundError("Learner not found")

        exam = Exam.objects.filter(pk=exam_id).first()
        if not exam:
            raise NotFoundError("Exam not found")

        existing_learner_exam = LearnerExam.objects.filter(
            learner=learner,
            exam=exam
        ).first()

        if existing_learner_exam:
            return existing_learner_exam

        learner_exam = LearnerExam.objects.create(
            learner=learner,
            exam=exam
        )

        return learner_exam

    def submit_exam(
            self,
            learner_id: int,
            exam_id: int
    ) -> LearnerExam:

        learner_exam = LearnerExam.objects.filter(
            learner_id=learner_id,
            exam_id=exam_id
        ).first()

        if not learner_exam:
            raise NotFoundError("Exam attempt not found")

        question_responses = QuestionResponse.objects.filter(
            exam_id=exam_id,
            learner_id=learner_id
        )

        total_score = 0
        for question_response in question_responses:
            if question_response.response.is_correct:
                total_score += question_response.question.score

        learner_exam.status = ExamStatus.ENDED.value
        learner_exam.score_obtained = total_score
        learner_exam.ended_at = timezone.now()
        learner_exam.save()

        return learner_exam

    def answer_question(
            self,
            exam_id: int,
            learner_id: int,
            question_id: int,
            option_id: int
    ) -> QuestionResponse:
        learner_exam = LearnerExam.objects.filter(
            learner_id=learner_id,
            exam_id=exam_id
        ).first()

        if not learner_exam:
            raise NotFoundError("Exam attempt not found")

        if learner_exam.status == ExamStatus.ENDED.value:
            raise ValueError("Exam attempt already completed")

        question_response = QuestionResponse.objects.create(
            exam=learner_exam.exam,
            question_id=question_id,
            learner_id=learner_id,
            response_id=option_id
        )

        return question_response
