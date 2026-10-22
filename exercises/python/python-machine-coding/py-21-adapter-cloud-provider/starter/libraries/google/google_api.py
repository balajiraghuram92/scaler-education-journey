import uuid
import datetime
from libraries.google.google_connection_response import GoogleConnectionResponse

class GoogleApi:
    def create_connection(self, user_id: int) -> GoogleConnectionResponse:
        response = GoogleConnectionResponse()
        response.connection_id = str(uuid.uuid4())
        response.connection_status = "SUCCESS"
        response.connection_date = datetime.datetime.now()
        return response
