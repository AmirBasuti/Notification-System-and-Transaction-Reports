from mongoengine import Document, StringField, FloatField

class TransactionSummary(Document):
    key = StringField()
    value = FloatField(default=0)
    type = StringField()
    mode = StringField()
    merchant_id = StringField(null=True)
    meta = {'collection': 'transaction_summary'}