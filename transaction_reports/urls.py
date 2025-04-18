from django.urls import path
from .views import TransactionReportAPIView, CachedTransactionReportAPIView

urlpatterns = [
    path('reports/', TransactionReportAPIView.as_view(), name='transaction-reports'),
    path('reports/cached/', CachedTransactionReportAPIView.as_view(), name='cached-transaction-reports'),
]