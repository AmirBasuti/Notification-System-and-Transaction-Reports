from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime
from .models import Notification, NotificationDelivery, Recipient, NotificationTemplate
from .serializers import NotificationSerializer, NotificationTemplateSerializer
from .tasks import send_notification


class SendNotificationView(APIView):
    def post(self, request):
        serializer = NotificationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        recipient_id = data['recipient_id']

        try:
            recipient = Recipient.objects.get(user_id=recipient_id)
        except Recipient.DoesNotExist:
            return Response(
                {'error': f'Recipient with ID {recipient_id} does not exist'},
                status=status.HTTP_404_NOT_FOUND
            )

        content = data.get('content')
        template = None

        if 'template_id' in data and data['template_id']:
            try:
                template = NotificationTemplate.objects.get(id=data['template_id'])
                content = template.content
            except NotificationTemplate.DoesNotExist:
                return Response(
                    {'error': f'Template with ID {data["template_id"]} does not exist'},
                    status=status.HTTP_404_NOT_FOUND
                )

        if not content:
            return Response(
                {'error': 'Either content or template_id must be provided'},
                status=status.HTTP_400_BAD_REQUEST
            )

        notification = Notification(
            recipient=recipient,
            template=template,
            content=content,
            mediums=data['mediums'],
            created_at=datetime.now()
        )
        notification.save()

        for medium in data['mediums']:
            delivery = NotificationDelivery(
                notification=notification,
                medium=medium,
                status='pending'
            )
            delivery.save()

            send_notification.delay(str(notification.id), medium, str(delivery.id))

        return Response({
            'id': str(notification.id),
            'message': 'Notification queued for delivery'
        }, status=status.HTTP_202_ACCEPTED)


class NotificationStatusView(APIView):
    def get(self, request, notification_id):
        try:
            notification = Notification.objects.get(id=notification_id)
        except Notification.DoesNotExist:
            return Response(
                {'error': f'Notification with ID {notification_id} does not exist'},
                status=status.HTTP_404_NOT_FOUND
            )

        deliveries = NotificationDelivery.objects(notification=notification)

        result = {
            'id': str(notification.id),
            'recipient': str(notification.recipient.id),
            'created_at': notification.created_at.isoformat(),
            'deliveries': [
                {
                    'medium': d.medium,
                    'status': d.status,
                    'sent_at': d.sent_at.isoformat() if d.sent_at else None,
                    'error_message': d.error_message,
                    'retry_count': d.retry_count
                }
                for d in deliveries
            ]
        }

        return Response(result)