from scaler.exceptions import InvalidBatchError, UserNotFoundError, UnauthorizedAccessError
from scaler.models import CommunicationLearner
from scaler.models import User, BatchLearner, Batch, Communication, UserType
from .communication_service import CommunicationService
from scaler.adapters import EmailAdapter, WhatsappAdapter


class CommunicationServiceImpl(CommunicationService):
    email_adapter: EmailAdapter
    whatsapp_adapter: WhatsappAdapter

    def __init__(
            self,
            email_adapter: EmailAdapter,
            whatsapp_adapter: WhatsappAdapter
    ):
        self.email_adapter = email_adapter
        self.whatsapp_adapter = whatsapp_adapter

    def broadcast_message(self, batch_id: int, sender_id: int, message: str) -> Communication:

        user = User.objects.filter(pk=sender_id).first()

        if user is None:
            raise UserNotFoundError("User not found")

        if user.user_type != UserType.INSTRUCTOR.value:
            raise UnauthorizedAccessError("User is not an instructor")

        batch = Batch.objects.filter(pk=batch_id).first()

        if batch is None:
            raise InvalidBatchError("Batch not found")

        communication = Communication.objects.create(
            batch=batch,
            sender=user,
            message=message
        )

        current_learners = BatchLearner.objects.filter(
            batch=batch,
            exit_date__isnull=True
        )

        for batch_learner in current_learners:
            self.email_adapter.send_email(
                batch_learner.learner.email,
                "Broadcast Message",
                message
            )
            self.whatsapp_adapter.send_whatsapp_message(
                batch_learner.learner.phone_number,
                message
            )

            CommunicationLearner.objects.create(
                communication=communication,
                learner=batch_learner.learner,
                sent_email=True,
                sent_sms=True
            )

        return communication





