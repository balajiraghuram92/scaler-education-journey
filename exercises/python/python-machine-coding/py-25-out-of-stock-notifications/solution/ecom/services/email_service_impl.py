from ecom.adapters.email_adapter import EmailAdapter
from ecom.models import Product, User
from ecom.services.email_service import EmailService


class EmailServiceImpl(EmailService):
    def __init__(self, email_adapter: EmailAdapter) -> None:
        self.email_adapter = email_adapter

    def notify_user(self, user: User, product: Product) -> bool:
        subject = f"Product Back in Stock: {product.name}"
        body = (f"Dear {user.name},\n\n"
                f"The product {product.name} is back in stock. Hurry up and place your order.\n\n"
                "Thanks,\nTeam Ecom\n")
        return self.email_adapter.send_email(user.email, subject, body)
