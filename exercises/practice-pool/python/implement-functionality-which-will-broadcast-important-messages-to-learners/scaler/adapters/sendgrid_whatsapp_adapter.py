from .whatsapp_adapter import WhatsappAdapter
from scaler.libs import send_whatsapp_message as send_whatsapp_message_with_sendgrid


class SendGridWhatsappAdapter(WhatsappAdapter):

    def send_whatsapp_message(self, phone, message):
        send_whatsapp_message_with_sendgrid(
            phone, message
        )

