from rest_framework import serializers

class TransactionReportSerializer(serializers.Serializer):
    key = serializers.CharField()
    value = serializers.FloatField()