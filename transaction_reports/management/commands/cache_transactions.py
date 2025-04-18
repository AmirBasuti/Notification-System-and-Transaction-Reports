# transaction_reports/management/commands/cache_transactions.py
from django.core.management.base import BaseCommand
from pymongo import MongoClient
from django.conf import settings
from transaction_reports.utils import get_transaction_report
from transaction_reports.models import TransactionSummary


class Command(BaseCommand):
    help = 'Cache transaction reports to improve performance'

    def handle(self, *args, **options):
        self.stdout.write('Caching transaction reports...')

        client = MongoClient(settings.MONGODB_HOST, settings.MONGODB_PORT)
        db = client[settings.MONGODB_DB]

        TransactionSummary.objects.all().delete()

        merchant_ids = [str(mid) for mid in db.transactions.distinct('merchantId')]
        merchant_ids.append(None)

        modes = ['daily', 'weekly', 'monthly']
        types = ['count', 'amount']

        for mode in modes:
            for type_param in types:
                for merchant_id in merchant_ids:
                    self.stdout.write(f'Processing {mode} {type_param} for merchant {merchant_id}')
                    report_data = get_transaction_report(type_param, mode, merchant_id)

                    for entry in report_data:
                        TransactionSummary(
                            key=entry['key'],
                            value=entry['value'],
                            type=type_param,
                            mode=mode,
                            merchant_id=merchant_id
                        ).save()

        self.stdout.write(self.style.SUCCESS('Successfully cached transaction reports'))