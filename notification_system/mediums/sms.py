import logging
from .base import NotificationMedium

logger = logging.getLogger(__name__)


class SMSMedium(NotificationMedium):
    def _send(self, recipient, content, **kwargs):
        phone = getattr(recipient, "phone", None)
        if not phone:
            return False, "No phone number provided"

        logger.info(f"Sending SMS to {phone}: {content}")

        return True, None

    def format_content(self, content, **kwargs):
        return content[:157] + "..." if len(content) > 160 else content
