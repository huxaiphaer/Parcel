import csv
import logging
import os

from celery import shared_task
from django.db import transaction

from .models import Article, Shipment

logger = logging.getLogger(__name__)


def process_csv_row(row, row_num):
    """
    Process a single CSV row - extracted for easier testing.

    :param row: Dictionary representing a row from the CSV file.
    :param row_num: Row number (1-based) for logging purposes.

    Returns: (shipment_created, article_created, error_message)
    """
    try:
        tracking_number = row["tracking_number"].strip()
        if not tracking_number:
            return False, False, f"Row {row_num}: Empty tracking number"

        # Create shipment
        shipment, shipment_created = Shipment.objects.get_or_create(
            tracking_number=tracking_number,
            defaults={
                "carrier": row.get("carrier", "").strip(),
                "sender_address": row.get("sender_address", "").strip(),
                "receiver_address": row.get("receiver_address", "").strip(),
                "status": row.get("status", "").strip(),
            },
        )

        # Create article
        article, article_created = Article.objects.get_or_create(
            shipment=shipment,
            sku=row.get("SKU", "").strip(),
            defaults={
                "name": row.get("article_name", "").strip(),
                "quantity": int(row.get("article_quantity", 0)),
                "price": float(row.get("article_price", 0.0)),
            },
        )

        return shipment_created, article_created, None

    except (ValueError, TypeError) as e:
        return False, False, f"Row {row_num}: Invalid data - {str(e)}"
    except Exception as e:
        return False, False, f"Row {row_num}: {str(e)}"


def process_batch(batch_rows, batch_start_index):
    """
    Process a batch of rows - extracted for easier testing.

    :param batch_rows: List of rows from the CSV file.
    :param batch_start_index: Starting index for the batch (used for logging).

    Returns: (shipments_created, articles_created, errors)
    """
    shipments_created = 0
    articles_created = 0
    errors = []

    try:
        with transaction.atomic():
            for idx, row in enumerate(batch_rows):
                row_num = batch_start_index + idx + 1

                shipment_created, article_created, error = process_csv_row(
                    row, row_num
                )

                if error:
                    errors.append(error)
                    logger.warning(error)
                else:
                    if shipment_created:
                        shipments_created += 1
                    if article_created:
                        articles_created += 1

            logger.info(
                f"Batch starting at row {batch_start_index + 1} completed successfully"
            )

    except Exception as e:
        batch_num = (batch_start_index // len(batch_rows)) + 1
        error_msg = f"Batch {batch_num} failed: {str(e)}"
        errors.append(error_msg)
        logger.error(error_msg)

    return shipments_created, articles_created, errors


def validate_csv_file(csv_path):
    """
    Validate CSV file exists and has required columns.

    :param csv_path: Path to the CSV file.

    Returns: (is_valid, error_message, required_columns)
    """
    required_columns = [
        "tracking_number",
        "carrier",
        "sender_address",
        "receiver_address",
        "status",
        "article_name",
        "article_quantity",
        "article_price",
        "SKU",
    ]

    if not os.path.exists(csv_path):
        return False, f"CSV file not found: {csv_path}", required_columns

    try:
        with open(csv_path, newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            missing_columns = set(required_columns) - set(
                reader.fieldnames or []
            )

            if missing_columns:
                return (
                    False,
                    f"Missing required columns: {', '.join(missing_columns)}",
                    required_columns,
                )

        return True, None, required_columns

    except Exception as e:
        return False, f"Error reading CSV file: {str(e)}", required_columns


@shared_task(bind=True, name="shipments.tasks.load_seed_data_task")
def load_seed_data_task(self, csv_path, batch_size=1000):
    """
    Load seed data from CSV in batches - always runs asynchronously.

    :param self: Reference to the task instance.
    :param csv_path: Path to the CSV file.
    :param batch_size: Number of rows to process in each batch.

    Refactored for better testability.
    """
    try:
        # Validate file
        is_valid, error_message, _ = validate_csv_file(csv_path)
        if not is_valid:
            logger.error(error_message)
            return {"success": False, "message": error_message}

        logger.info(f"Starting seed data loading from {csv_path}")

        total_rows = 0
        total_shipments_created = 0
        total_articles_created = 0
        all_errors = []

        with open(csv_path, newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            rows = list(reader)
            total_rows = len(rows)

            logger.info(
                f"Processing {total_rows} rows in batches of {batch_size}"
            )

            # Process in batches
            for i in range(0, len(rows), batch_size):
                batch = rows[i : i + batch_size]
                batch_num = (i // batch_size) + 1

                shipments_created, articles_created, errors = process_batch(
                    batch, i
                )

                total_shipments_created += shipments_created
                total_articles_created += articles_created
                all_errors.extend(errors)

                # Update progress
                self.update_state(
                    state="PROGRESS",
                    meta={
                        "current": min(i + batch_size, total_rows),
                        "total": total_rows,
                        "batch": batch_num,
                    },
                )

        # Final results
        success_msg = (
            f"Seed data loaded successfully! "
            f"Processed: {total_rows} rows, "
            f"Created: {total_shipments_created} shipments, {total_articles_created} articles"
        )

        if all_errors:
            success_msg += f" (with {len(all_errors)} errors)"
            logger.warning(f"Completed with {len(all_errors)} errors")

        logger.info(success_msg)

        return {
            "success": True,
            "message": success_msg,
            "total_rows": total_rows,
            "shipments_created": total_shipments_created,
            "articles_created": total_articles_created,
            "errors": len(all_errors),
        }

    except Exception as e:
        error_msg = f"Task failed: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return {"success": False, "message": error_msg}
