from django.test import TestCase

from django.test import TestCase

from scaler.controllers import BatchController
from scaler.dtos import AddLearnerToBatchResDto, AddLearnerToBatchReqDto, ResponseStatus
from scaler.dtos import RemoveLearnerFromBatchReqDto, RemoveLearnerFromBatchResDto
from scaler.models import Batch, Learner, User, UserType
from scaler.services import BatchServiceImpl


class TestBatchController(TestCase):

    def setUp(self):
        self.batch_service = BatchServiceImpl()
        self.batch_controller = BatchController(
            batch_service=self.batch_service
        )
        self.generate_data()

    def test_add_learner_success(self):
        admin = self.data["admin"]
        learner = self.data["learner"]
        batch = self.data["batch"]

        response_dto: AddLearnerToBatchResDto = self.batch_controller.add_learner_to_batch(
            request_dto=AddLearnerToBatchReqDto(
                admin_id=admin.id,
                learner_id=learner.id,
                batch_id=batch.id
            )
        )

        assert response_dto.response_status == ResponseStatus.SUCCESS
        learner_batch = response_dto.batch_learner
        assert learner_batch.learner == learner
        assert learner_batch.batch == batch
        assert learner_batch.exit_date is None
        assert learner_batch.entry_date is not None

    def test_add_learner_failure_remove_before_add(self):
        admin = self.data["admin"]
        learner = self.data["learner"]
        batch = self.data["batch"]

        response_dto: RemoveLearnerFromBatchResDto = self.batch_controller.remove_learner_from_batch(
            request_dto=RemoveLearnerFromBatchReqDto(
                admin_id=admin.id,
                learner_id=learner.id,
                batch_id=batch.id
            )
        )

        assert response_dto.response_status == ResponseStatus.FAILURE

    def test_add_learner_failure_invalid_admin(self):
        learner = self.data["learner"]
        batch = self.data["batch"]

        response_dto: RemoveLearnerFromBatchResDto = self.batch_controller.remove_learner_from_batch(
            request_dto=RemoveLearnerFromBatchReqDto(
                admin_id=100,
                learner_id=learner.id,
                batch_id=batch.id
            )
        )

        assert response_dto.response_status == ResponseStatus.FAILURE

    def test_add_learner_failure_invalid_learner(self):
        admin = self.data["admin"]
        batch = self.data["batch"]
        response_dto: RemoveLearnerFromBatchResDto = self.batch_controller.remove_learner_from_batch(
            request_dto=RemoveLearnerFromBatchReqDto(
                admin_id=admin.id,
                learner_id=100,
                batch_id=batch.id
            )
        )

        assert response_dto.response_status == ResponseStatus.FAILURE

    def test_add_learner_failure_invalid_batch(self):
        admin = self.data["admin"]
        learner = self.data["learner"]
        response_dto: RemoveLearnerFromBatchResDto = self.batch_controller.remove_learner_from_batch(
            request_dto=RemoveLearnerFromBatchReqDto(
                admin_id=admin.id,
                learner_id=learner.id,
                batch_id=100
            )
        )

        assert response_dto.response_status == ResponseStatus.FAILURE

    def generate_data(self):
        admin = User.objects.create(
            name="Admin",
            email="admin@scaler.com",
            phone="1234567890",
            user_type=UserType.ADMIN
        )

        learner = Learner.objects.create(
            name="Learner1",
            email="learner1@gmail.com",
            phone="1234567890"
        )

        batch = Batch.objects.create(
            name="Batch1"
        )

        self.data = {
            "admin": admin,
            "learner": learner,
            "batch": batch
        }
