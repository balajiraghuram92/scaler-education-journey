from django.test import TestCase

from scaler.models import Batch, User, Learner, CommunicationLearner, Communication, BatchLearner, Batch, UserType
from scaler.services import CommunicationServiceImpl
from scaler.adapters import SendGridEmailAdapter, SendGridWhatsappAdapter


class TestCommunicationService(TestCase):

    def setUp(self):
        self.email_adapter = SendGridEmailAdapter()
        self.whatsapp_adapter = SendGridWhatsappAdapter()
        self.communication_service = CommunicationServiceImpl(
            email_adapter=self.email_adapter,
            whatsapp_adapter=self.whatsapp_adapter
        )
        self.generate_data()

    def test_broadcast_success(self):
        instructor = self.data["instructor"][0]
        batch = self.data["batches"][0]
        message = "Hello Learners"

        response = self.communication_service.broadcast_message(
            batch_id=batch.pk,
            sender_id=instructor.pk,
            message=message
        )

        count = CommunicationLearner.objects.filter(communication=response).count()

        assert count == 20, "Communication is not broadcast to all learners"
        assert response.batch == batch, "Batch is not equal to the scheduled batch"
        assert response.__class__ == Communication, "Response is not an instance of Communication"

    def generate_data(self):

        learners = []

        for i in range(40):
            learner = Learner.objects.create(
                name="Learner" + str(i),
                email="learner" + str(i) + "@gmail.com",
                phone_number="1234567890"
            )
            learners.append(learner)

        batch1 = Batch.objects.create(
            name="Batch1"
        )

        batch2 = Batch.objects.create(
            name="Batch2"
        )

        for learner in learners[:20]:
            BatchLearner.objects.create(
                batch=batch1,
                learner=learner
            )

        for learner in learners[20:]:
            BatchLearner.objects.create(
                batch=batch2,
                learner=learner
            )

        instructor1 = User.objects.create(
            name="Instructor1",
            email="inst1@gmail.com",
            user_type=UserType.INSTRUCTOR
        )

        self.data = {
            "instructor": [instructor1],
            "batches": [batch1, batch2],
            "learners": learners
        }



