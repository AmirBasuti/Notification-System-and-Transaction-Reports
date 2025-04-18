from django.urls import path
from .views import SendNotificationView, NotificationStatusView

urlpatterns = [
    path('send/', SendNotificationView.as_view(), name='send-notification'),
    path('status/<str:notification_id>/', NotificationStatusView.as_view(), name='notification-status'),
]