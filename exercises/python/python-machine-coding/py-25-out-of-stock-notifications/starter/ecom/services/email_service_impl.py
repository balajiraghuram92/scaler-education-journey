from ecom.adapters.email_adapter import EmailAdapter
from ecom.models import Product, User
from ecom.services.email_service import EmailService

class EmailServiceImpl(EmailService):

    def __init__(self, email_adapter: EmailAdapter) -> None:
        """Keep the email adapter."""
        raise NotImplementedError('TODO: implement __init__')

    def notify_user(self, user: User, product: Product) -> bool:
        """Send one email to user.email through the adapter: the subject names the product and says it is back in stock, the body addresses the user by name. Return the adapter result."""
        raise NotImplementedError('TODO: implement notify_user')
