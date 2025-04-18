from .mediums.sms import SMSMedium
from .mediums.email import EmailMedium
from .mediums.telegram import TelegramMedium

class NotificationMediumFactory:
    @staticmethod
    def get_medium(medium_type):
        if medium_type == 'sms':
            return SMSMedium()
        elif medium_type == 'email':
            return EmailMedium()
        elif medium_type == 'telegram':
            return TelegramMedium()
        else:
            raise ValueError(f"Unsupported medium type: {medium_type}")