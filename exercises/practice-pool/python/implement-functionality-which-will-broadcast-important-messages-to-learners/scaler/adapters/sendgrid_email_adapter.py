from .email_adapter import EmailAdapter
from scaler.libs import send_email as send_email_with_sendgrid


class SendGridEmailAdapter(EmailAdapter):

    def send_email(self, email, subject, message):
        send_email_with_sendgrid(email, subject, message)
