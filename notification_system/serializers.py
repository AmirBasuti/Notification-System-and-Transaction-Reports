from rest_framework import serializers

class NotificationSerializer(serializers.Serializer):
    recipient_id = serializers.CharField(required=True)
    template_id = serializers.CharField(required=False)
    content = serializers.CharField(required=False)
    mediums = serializers.ListField(
        child=serializers.CharField(),
        required=True
    )

class NotificationTemplateSerializer(serializers.Serializer):
    name = serializers.CharField(required=True)
    content = serializers.CharField(required=True)