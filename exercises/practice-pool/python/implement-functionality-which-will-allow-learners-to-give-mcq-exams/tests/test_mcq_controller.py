from django.test import TestCase

from scaler.controllers import MCQExamController
from scaler.dtos import StartExamReqDto, StartExamResDto, ResponseStatus, SubmitExamReqDto, AnswerQuestionReqDto
from scaler.exceptions import NotFoundError
from scaler.models import Learner, Exam, Question, Option, LearnerExam
from scaler.services import MCQExamServiceImpl


class TestMCQExamController(TestCase):

    def setUp(self):
        self.mcq_exam_service = MCQExamServiceImpl()
        self.mcq_exam_controller = MCQExamController(self.mcq_exam_service)
        self.generate_data()

    def test_success_exam_start(self):
        learner = self.data["learners"][0]
        exam = self.data["exam"]

        response_dto: StartExamResDto = self.mcq_exam_controller.start_exam(
            request_dto=StartExamReqDto(
                exam_id=exam.pk,
                learner_id=learner.pk
            )
        )

        assert response_dto.response_status == ResponseStatus.SUCCESS

        learner_exam = response_dto.learner_exam
        assert learner_exam.__class__ == LearnerExam
        assert learner_exam.learner == learner
        assert learner_exam.exam == exam

    def test_success_exam_start_twice(self):
        learner = self.data["learners"][0]
        exam = self.data["exam"]

        response_dto1: StartExamResDto = self.mcq_exam_controller.start_exam(
            request_dto=StartExamReqDto(
                exam_id=exam.pk,
                learner_id=learner.pk
            )
        )

        response_dto2: StartExamResDto = self.mcq_exam_controller.start_exam(
            request_dto=StartExamReqDto(
                exam_id=exam.pk,
                learner_id=learner.pk
            )
        )

        assert response_dto1.response_status == ResponseStatus.SUCCESS
        assert response_dto2.response_status == ResponseStatus.SUCCESS
        assert response_dto1.learner_exam.pk == response_dto2.learner_exam.pk

    def test_end_without_start(self):
        learner = self.data["learners"][0]
        exam = self.data["exam"]

        response_dto = self.mcq_exam_controller.submit_exam(
            request_dto=SubmitExamReqDto(
                exam_id=exam.pk,
                learner_id=learner.pk
            )
        )

        assert response_dto.response_status == ResponseStatus.FAILURE

    def test_success_complete_walk(self):
        learner = self.data["learners"][0]
        exam = self.data["exam"]

        response_dto: StartExamResDto = self.mcq_exam_controller.start_exam(
            request_dto=StartExamReqDto(
                exam_id=exam.pk,
                learner_id=learner.pk
            )
        )

        assert response_dto.response_status == ResponseStatus.SUCCESS

        for question, correct_option in self.data["questions"]:
            answer_response_dto = self.mcq_exam_controller.answer_question(
                request_dto=AnswerQuestionReqDto(
                    exam_id=exam.pk,
                    learner_id=learner.pk,
                    question_id=question.pk,
                    option_id=correct_option.pk
                )
            )
            assert answer_response_dto.response_status == ResponseStatus.SUCCESS

        response_dto = self.mcq_exam_controller.submit_exam(
            request_dto=SubmitExamReqDto(
                exam_id=exam.pk,
                learner_id=learner.pk
            )
        )

        assert response_dto.response_status == ResponseStatus.SUCCESS

        learner_exam = response_dto.learner_exam
        assert learner_exam.status == "ENDED"
        assert learner_exam.score_obtained == 3.0

    def generate_data(self):
        exam = Exam.objects.create(
            name="Python Exam 1",
        )

        question1 = Question.objects.create(
            description="Is Python case sensitive when dealing with identifiers?",
            exam=exam,
            score=1.0
        )

        q1o1 = Option.objects.create(
            text="yes",
            question=question1,
            is_correct=True
        )

        q1o2 = Option.objects.create(
            text="no",
            question=question1,
            is_correct=False
        )

        question2 = Question.objects.create(
            description="Which of the following is an invalid variable?",
            exam=exam,
            score=1.0
        )

        q2o1 = Option.objects.create(
            text="my_string_1",
            question=question2,
            is_correct=False
        )

        q2o2 = Option.objects.create(
            text="1st_string",
            question=question2,
            is_correct=True
        )

        question3 = Question.objects.create(
            description="Which of the following is an invalid statement?",
            exam=exam,
            score=1.0
        )

        q3o1 = Option.objects.create(
            text="abc = 1,000,000",
            question=question3,
            is_correct=False
        )

        q3o2 = Option.objects.create(
            text="a b c = 1000 2000 3000",
            question=question3,
            is_correct=True
        )

        learner = Learner.objects.create(
            name="Learner1",
            email="learner1@gmail.com",
            phone="1234567890"
        )

        self.data = {
            "exam": exam,
            "questions": [(question1, q1o1), (question2, q2o2), (question3, q3o2)],
            "learners": [learner]
        }
