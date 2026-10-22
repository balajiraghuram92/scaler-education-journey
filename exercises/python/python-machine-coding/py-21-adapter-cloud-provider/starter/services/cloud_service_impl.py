from services.cloud_service import CloudService
from adapters.cloud_adapter import CloudAdapter
from repositories.user_repository import UserRepository
from models.connection import Connection
from exceptions.exceptions import UserNotFoundException

class CloudServiceImpl(CloudService):

    def __init__(self, cloud_adapter: CloudAdapter, user_repository: UserRepository):
        """Keep the injected adapter and user repository."""
        raise NotImplementedError('TODO: implement __init__')

    def create_connection(self, user_id: int) -> Connection:
        """Raise UserNotFoundException("User not found") for an unknown user, otherwise return what the adapter creates."""
        raise NotImplementedError('TODO: implement create_connection')
