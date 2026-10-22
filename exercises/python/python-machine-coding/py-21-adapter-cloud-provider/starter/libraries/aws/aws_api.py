import uuid
import datetime
from libraries.aws.aws_connection_response import AWSConnectionResponse

class AWSApi:
    def create_connection(self, user_id: int) -> AWSConnectionResponse:
        response = AWSConnectionResponse()
        response.connection_id = str(uuid.uuid4())
        response.connection_status = "SUCCESS"
        response.connection_date = datetime.datetime.now()
        return response
