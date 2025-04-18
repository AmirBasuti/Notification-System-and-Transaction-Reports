from celery import shared_task
from datetime import datetime
from .models import Notification, NotificationDelivery
from .factory import NotificationMediumFactory
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def send_notification(self, notification_id, medium_type, delivery_id):
    try:
        notification = Notification.objects.get(id=notification_id)
        delivery = NotificationDelivery.objects.get(id=delivery_id)

        if delivery.status == 'sent':
            logger.info(f"Notification {notification_id} already sent via {medium_type}")
            return

        medium = NotificationMediumFactory.get_medium(medium_type)
        success, error_message = medium.send(notification.recipient, notification.content)

        if success:
            delivery.status = 'sent'
            delivery.sent_at = datetime.now()
            delivery.save()
            logger.info(f"Successfully sent notification {notification_id} via {medium_type}")
        else:
            delivery.retry_count += 1
            delivery.error_message = error_message

            if delivery.retry_count >= 3:
                delivery.status = 'failed'
                logger.error(f"Failed to send notification {notification_id} via {medium_type} after 3 retries")
            else:
                logger.warning(f"Failed to send notification {notification_id} via {medium_type}, will retry")
                delivery.save()
                retry_in = 60 * (2 ** (delivery.retry_count - 1))  # 1 min, 2 min, 4 min
                self.retry(countdown=retry_in)
                return

            delivery.save()
    except Exception as e:
        logger.exception(f"Error sending notification {notification_id} via {medium_type}: {str(e)}")
        if self.request.retries < self.max_retries:
            self.retry(countdown=60 * (2 ** self.request.retries))
        else:
            try:
                delivery = NotificationDelivery.objects.get(id=delivery_id)
                delivery.status = 'failed'
                delivery.error_message = str(e)
                delivery.save()
            except:
                pass