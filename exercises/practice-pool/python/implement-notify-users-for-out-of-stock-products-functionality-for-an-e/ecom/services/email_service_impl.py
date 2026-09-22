from .email_service import EmailService
from ecom.adapters.email_adapter import EmailAdapter
from ..models import User, Product


class EmailServiceImpl(EmailService):
    email_adapter: EmailAdapter

    def __init__(self, email_adapter: EmailAdapter):
        self.email_adapter = email_adapter

    def notify_user(
            self,
            user: User,
            product: Product
    ) -> bool:

        to = user.email
        subject = f"Product Back in Stock: {product.name}"
        body = f"""
        Dear {user.name},
        
        The product {product.name} is back in stock. Hurry up and place your order.
        
        Thanks,
        Team Ecom
        """

        return self.email_adapter.send_email(to, subject, body)
