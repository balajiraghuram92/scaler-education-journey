from services.cloud_service import CloudService
from adapters.cloud_adapter import CloudAdapter
from repositories.user_repository import UserRepository
from models.connection import Connection
from exceptions.exceptions import UserNotFoundException

class CloudServiceImpl(CloudService):
    def __init__(self, cloud_adapter: CloudAdapter, user_repository: UserRepository):
        self.cloud_adapter = cloud_adapter
        self.user_repository = user_repository

    def create_connection(self, user_id: int) -> Connection:
        user = self.user_repository.find_user_by_id(user_id)
        if not user:
            raise UserNotFoundException("User not found")
            
        connection = self.cloud_adapter.create_connection(user_id)
        return connection
