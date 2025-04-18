import logging
# from django.core.mail import send_mail

from .base import NotificationMedium

logger = logging.getLogger(__name__)


class EmailMedium(NotificationMedium):
    def _send(self, recipient, content, **kwargs):
        email = getattr(recipient, "email", None)
        if not email:
            return False, "No email address provided"

        #  for real email sending, uncomment the following lines

        # subject = kwargs.get("subject", "Notification")
        # try:
        #     send_mail(
        #         subject=subject,
        #         message="",
        #         html_message=content,
        #         from_email=None,
        #         recipient_list=[email],
        #         fail_silently=False,
        #     )
        #     logger.info(f"Sent email to {email}")
        #     return True, None
        # except Exception as exc:
        #     logger.exception("Email sending failed")
        #     return False, str(exc)

        logger.info(f"Sending email to {email}: {content}")
        return True, None

    def format_content(self, content, **kwargs):
        return f"<html><body>{content}</body></html>"
