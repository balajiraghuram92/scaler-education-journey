from adapters.cloud_adapter import CloudAdapter
from libraries.google.google_api import GoogleApi
from models.connection import Connection
from models.enums import ConnectionStatus

class GoogleCloudAdapter(CloudAdapter):

    def __init__(self):
        """Create the GoogleApi SDK object and keep it."""
        raise NotImplementedError('TODO: implement __init__')

    def create_connection(self, user_id: int) -> Connection:
        """Call the SDK, then build a domain Connection: connection_id from the response, user_id from the argument, and connection_status SUCCESS only when the response status is "SUCCESS" (otherwise FAILURE)."""
        raise NotImplementedError('TODO: implement create_connection')
