import csv
import os
from django.core.management.base import BaseCommand, CommandError
from shipments.models import Shipment, Article

class Command(BaseCommand):
    help = "Load shipments and articles from a CSV file"

    def add_arguments(self, parser):
        parser.add_argument(
            '--csv',
            type=str,
            help='Path to the CSV file containing shipment data',
            required=True
        )

    def handle(self, *args, **options):
        csv_path = options['csv']

        if not os.path.exists(csv_path):
            raise CommandError(f"CSV file not found: {csv_path}")

        with open(csv_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                shipment, _ = Shipment.objects.get_or_create(
                    tracking_number=row['tracking_number'],
                    carrier=row['carrier'],
                    sender_address=row['sender_address'],
                    receiver_address=row['receiver_address'],
                    status=row['status'],
                )
                Article.objects.get_or_create(
                    shipment=shipment,
                    name=row['article_name'],
                    quantity=int(row['article_quantity']),
                    price=float(row['article_price']),
                    sku=row['SKU'],
                )

        self.stdout.write(self.style.SUCCESS(f'Seed data loaded successfully from {csv_path}'))
