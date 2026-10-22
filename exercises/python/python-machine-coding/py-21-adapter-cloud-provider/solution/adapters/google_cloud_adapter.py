from adapters.cloud_adapter import CloudAdapter
from libraries.google.google_api import GoogleApi
from models.connection import Connection
from models.enums import ConnectionStatus

class GoogleCloudAdapter(CloudAdapter):
    def __init__(self):
        self.google_api = GoogleApi()

    def create_connection(self, user_id: int) -> Connection:
        google_response = self.google_api.create_connection(user_id)
        
        connection = Connection()
        connection.connection_id = google_response.connection_id
        connection.user_id = user_id
        
        if google_response.connection_status == "SUCCESS":
            connection.connection_status = ConnectionStatus.SUCCESS
        else:
            connection.connection_status = ConnectionStatus.FAILURE
            
        return connection
