from django.test import TestCase
from scaler.exceptions import NotFoundError
from scaler.models import Learner, Exam, Question, Option, LearnerExam
from scaler.services import MCQExamServiceImpl


class TestMCQExamService(TestCase):

    def setUp(self):
        self.learner_service = MCQExamServiceImpl()
        self.generate_data()

    def test_success_exam_start(self):
        learner = self.data["learners"][0]
        exam = self.data["exam"]

        learner_exam = self.learner_service.start_exam(
            learner_id=learner.pk,
            exam_id=exam.pk
        )

        assert learner_exam.__class__ == LearnerExam
        assert learner_exam.learner == learner
        assert learner_exam.exam == exam

    def test_success_exam_start_twice(self):
        learner = self.data["learners"][0]
        exam = self.data["exam"]

        learner_exam1 = self.learner_service.start_exam(
            learner_id=learner.pk,
            exam_id=exam.pk
        )

        learner_exam2 = self.learner_service.start_exam(
            learner_id=learner.pk,
            exam_id=exam.pk
        )

        assert learner_exam1.pk == learner_exam2.pk

    def test_end_without_start(self):
        learner = self.data["learners"][0]
        exam = self.data["exam"]

        with self.assertRaises(NotFoundError):
            learner_exam1 = self.learner_service.submit_exam(
                learner_id=learner.pk,
                exam_id=exam.pk
            )

    def test_success_complete_walk(self):
        learner = self.data["learners"][0]
        exam = self.data["exam"]

        learner_exam = self.learner_service.start_exam(
            learner_id=learner.pk,
            exam_id=exam.pk
        )

        for question, correct_option in self.data["questions"]:
            self.learner_service.answer_question(
                exam_id=exam.pk,
                learner_id=learner.pk,
                question_id=question.pk,
                option_id=correct_option.pk
            )

        learner_exam = self.learner_service.submit_exam(
            learner_id=learner.pk,
            exam_id=exam.pk
        )

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
