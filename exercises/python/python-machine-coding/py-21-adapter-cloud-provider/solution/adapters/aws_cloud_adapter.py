from adapters.cloud_adapter import CloudAdapter
from libraries.aws.aws_api import AWSApi
from models.connection import Connection
from models.enums import ConnectionStatus

class AWSCloudAdapter(CloudAdapter):
    def __init__(self):
        self.aws_api = AWSApi()

    def create_connection(self, user_id: int) -> Connection:
        aws_response = self.aws_api.create_connection(user_id)
        
        connection = Connection()
        connection.connection_id = aws_response.connection_id
        connection.user_id = user_id
        
        if aws_response.connection_status == "SUCCESS":
            connection.connection_status = ConnectionStatus.SUCCESS
        else:
            connection.connection_status = ConnectionStatus.FAILURE
            
        return connection
