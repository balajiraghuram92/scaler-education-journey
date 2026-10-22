from ecom.adapters.email_adapter import EmailAdapter
from ecom.libs import sendgrid

class EmailAdapterImpl(EmailAdapter):

    def send_email(self, to: str, subject: str, body: str) -> bool:
        """Call sendgrid.send_email(to, subject, body) (via the module, as imported) and return its result."""
        raise NotImplementedError('TODO: implement send_email')
