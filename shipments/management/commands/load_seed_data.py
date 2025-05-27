import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Parcels.settings")

from django.core.management.base import BaseCommand, CommandError

from shipments.tasks import load_seed_data_task


class Command(BaseCommand):
    help = "Load shipments and articles from CSV using async Celery task"

    def add_arguments(self, parser):
        parser.add_argument(
            "--csv",
            type=str,
            help="Path to the CSV file containing shipment data",
            required=True,
        )

    def handle(self, *args, **options):
        csv_path = options["csv"]

        if not os.path.exists(csv_path):
            raise CommandError(f"CSV file not found: {csv_path}")

        self.stdout.write(f"Starting async seed data loading from {csv_path}")

        task = load_seed_data_task.delay(csv_path)

        self.stdout.write(
            self.style.SUCCESS(
                f"Task started successfully!\n" f"Task ID: {task.id}\n"
            )
        )
