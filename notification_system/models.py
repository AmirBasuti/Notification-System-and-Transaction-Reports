from mongoengine import Document, StringField, ListField, DateTimeField, BooleanField, ReferenceField, DictField, IntField

class NotificationTemplate(Document):
    name = StringField(required=True)
    content = StringField(required=True)
    meta = {'collection': 'notification_templates'}

class Recipient(Document):
    user_id = StringField(primary_key=True)
    email = StringField()
    phone = StringField()
    telegram_id = StringField()
    meta = {'collection': 'recipients'}

class Notification(Document):
    recipient = ReferenceField(Recipient)
    template = ReferenceField(NotificationTemplate)
    content = StringField(required=True)
    mediums = ListField(StringField())
    created_at = DateTimeField()
    meta = {'collection': 'notifications'}

class NotificationDelivery(Document):
    notification = ReferenceField(Notification)
    medium = StringField(required=True)
    status = StringField(default='pending')
    sent_at = DateTimeField()
    error_message = StringField()
    retry_count = IntField(default=0)
    metadata = DictField()
    meta = {'collection': 'notification_deliveries'}