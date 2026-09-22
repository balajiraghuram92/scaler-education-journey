from abc import ABC, abstractmethod


class WhatsappAdapter(ABC):

    @abstractmethod
    def send_whatsapp_message(self, phone, message):
        pass
