import logging

from .base import NotificationMedium

logger = logging.getLogger(__name__)


class TelegramMedium(NotificationMedium):
    def _send(self, recipient, content, **kwargs):
        telegram_id = getattr(recipient, "telegram_id", None)
        if not telegram_id:
            return False, "No Telegram ID provided"

        logger.info(f"Sending Telegram message to {telegram_id}: {content}")

        return True, None

    # ---------- فرمت مخصوص تلگرام (Markdown مثلاً) ----------
    def format_content(self, content, **kwargs):
        return content
