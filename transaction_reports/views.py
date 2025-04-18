from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import TransactionSummary
from .serializers import TransactionReportSerializer
from .utils import get_transaction_report


VALID_TYPES = ["count", "amount"]
VALID_MODES = ["daily", "weekly", "monthly"]

CACHE_TTL = getattr(settings, "TRANSACTION_REPORT_CACHE_TTL", 600)


class TransactionReportAPIView(APIView):
    def get(self, request):
        report_type = request.query_params.get("type", "count")
        if report_type not in VALID_TYPES:
            return Response(
                {"detail": "type must be 'count' or 'amount'"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        mode = request.query_params.get("mode", "daily")
        if mode not in VALID_MODES:
            return Response(
                {"detail": "mode must be 'daily', 'weekly' or 'monthly'"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        merchant_id = request.query_params.get("merchantId")

        data = get_transaction_report(report_type, mode, merchant_id)

        serializer = TransactionReportSerializer(data, many=True)
        return Response(serializer.data)


@method_decorator(cache_page(CACHE_TTL), name="dispatch")
class CachedTransactionReportAPIView(APIView):
     def get(self, request):
        report_type = request.query_params.get("type", "count")
        if report_type not in VALID_TYPES:
            return Response(
                {"detail": "type must be 'count' or 'amount'"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        mode = request.query_params.get("mode", "daily")
        if mode not in VALID_MODES:
            return Response(
                {"detail": "mode must be 'daily', 'weekly' or 'monthly'"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        merchant_id = request.query_params.get("merchantId")

        filters = {"type": report_type, "mode": mode}
        if merchant_id:
            filters["merchant_id"] = merchant_id

        queryset = TransactionSummary.objects.filter(**filters).order_by("key")

        data = [{"key": obj.key, "value": obj.value} for obj in queryset]

        serializer = TransactionReportSerializer(data, many=True)
        return Response(serializer.data)
