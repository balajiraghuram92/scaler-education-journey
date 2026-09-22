from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from scaler.models import Batch, Learner, BatchLearner, User, UserType
from scaler.services import BatchServiceImpl
from scaler.exceptions import NotFoundError, UnauthorizedAccessError


class TestBatchService(TestCase):

    def setUp(self):

        self.batch_service = BatchServiceImpl()
        self.generate_data()

    def test_add_learner_success(self):
        admin = self.data["admin"]
        learner = self.data["learner"]
        batch = self.data["batch"]

        learner_batch = self.batch_service.add_learner_to_batch(
            admin_id=admin.id,
            learner_id=learner.id,
            batch_id=batch.id
        )

        assert learner_batch.learner == learner
        assert learner_batch.batch == batch
        assert learner_batch.exit_date is None
        assert learner_batch.entry_date is not None

    def test_add_learner_failure_invalid_admin(self):
        admin = self.data["admin"]
        learner = self.data["learner"]
        batch = self.data["batch"]

        with self.assertRaises(NotFoundError):
            learner_batch = self.batch_service.add_learner_to_batch(
                admin_id=100,
                learner_id=learner.id,
                batch_id=batch.id
            )

        with self.assertRaises(NotFoundError):
            learner_batch = self.batch_service.add_learner_to_batch(
                admin_id=admin.id,
                learner_id=100,
                batch_id=batch.id
            )

        with self.assertRaises(UnauthorizedAccessError):
            learner_batch = self.batch_service.add_learner_to_batch(
                admin_id=learner.id,
                learner_id=learner.id,
                batch_id=batch.id
            )

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
