from datetime import timezone

from .batch_service import BatchService
from typing import List, Optional

from scaler.models import User, Learner, BatchLearner, Batch, UserType
from scaler.exceptions import UnauthorizedAccessError, NotFoundError


class BatchServiceImpl(BatchService):

        def add_learner_to_batch(
                self,
                admin_id: int,
                learner_id: int,
                batch_id: int,
        ) -> BatchLearner:

            admin = User.objects.filter(id=admin_id).first()
            learner = Learner.objects.filter(id=learner_id).first()
            batch = Batch.objects.filter(id=batch_id).first()

            if not admin or not learner or not batch:
                raise NotFoundError('Admin, learner or batch not found')

            if admin.user_type != UserType.ADMIN.value:
                raise UnauthorizedAccessError('Only admin can add learner to batch')

            existing_batch_learner = BatchLearner.objects.filter(
                learner=learner,
                batch=batch
            ).first()

            if existing_batch_learner:
                return existing_batch_learner

            batch_learner = BatchLearner.objects.create(
                learner=learner,
                batch=batch
            )
            return batch_learner

        def remove_learner_from_batch(
                self,
                admin_id: int,
                learner_id: int,
                batch_id: int,
        ) -> Optional[BatchLearner]:

            admin = User.objects.filter(id=admin_id).first()
            learner = Learner.objects.filter(id=learner_id).first()
            batch = Batch.objects.filter(id=batch_id).first()

            if not admin or not learner or not batch:
                raise NotFoundError('Admin, learner or batch not found')

            if admin.user_type != UserType.ADMIN.value:
                raise UnauthorizedAccessError('Only admin can remove learner from batch')

            batch_learner = BatchLearner.objects.filter(
                learner=learner,
                batch=batch
            ).first()

            if batch_learner:
                batch_learner.exit_date = timezone.now()
                batch_learner.save()
                return batch_learner
            else:
                raise NotFoundError('Learner is not enrolled in the batch')