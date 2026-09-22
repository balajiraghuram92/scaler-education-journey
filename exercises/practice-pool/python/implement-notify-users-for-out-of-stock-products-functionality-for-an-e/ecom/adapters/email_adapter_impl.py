from .email_adapter import EmailAdapter
from ecom.libs import sendgrid


class EmailAdapterImpl(EmailAdapter):

    def send_email(
            self,
            to: str,
            subject: str,
            body: str
    ) -> bool:
        return sendgrid.send_email(to, subject, body)
