import csv
import os
import tempfile
from decimal import Decimal

import pytest
from django.test import TransactionTestCase

from shipments.models import Article, Shipment
from shipments.tasks import load_seed_data_task


@pytest.mark.integration
@pytest.mark.django_db
class TestCeleryTaskIntegration:

    def test_successful_task_execution(self, temp_csv_file):
        """Test successful execution of the full task end-to-end"""

        result = load_seed_data_task.apply(
            args=[temp_csv_file], kwargs={"batch_size": 1}
        )
        task_result = result.result

        # Verify task results
        assert task_result["success"] == True
        assert task_result["total_rows"] == 2
        assert task_result["shipments_created"] == 2
        assert task_result["articles_created"] == 2
        assert task_result["errors"] == 0

        assert Shipment.objects.count() == 2
        assert Article.objects.count() == 2

        shipment = Shipment.objects.get(tracking_number="TN001")
        assert shipment.carrier == "DHL"
        assert shipment.status == "in_transit"

        article = Article.objects.get(sku="SKU001")
        assert article.name == "Test Product"
        assert article.quantity == 2
        assert article.price == Decimal("29.99")

    def test_task_with_invalid_file(self):
        """Test task execution with invalid file path"""
        result = load_seed_data_task.apply(args=["nonexistent.csv"])
        task_result = result.result

        assert task_result["success"] == False
        assert "CSV file not found" in task_result["message"]

        assert Shipment.objects.count() == 0
        assert Article.objects.count() == 0

    def test_task_with_large_file(self, large_csv_file):
        """Test task execution with large file (performance test)"""
        result = load_seed_data_task.apply(
            args=[large_csv_file], kwargs={"batch_size": 20}
        )
        task_result = result.result

        assert task_result["success"] == True
        assert task_result["total_rows"] == 1000
        assert task_result["shipments_created"] == 1000
        assert task_result["articles_created"] == 1000
        assert task_result["errors"] == 0

        assert Shipment.objects.count() == 1000
        assert Article.objects.count() == 1000


class TestTaskIntegrationWithUnittest(TransactionTestCase):
    """Integration tests using Django's unittest style"""

    def setUp(self):
        """Set up test data"""
        self.temp_files = []

    def tearDown(self):
        """Clean up temporary files"""
        for temp_file in self.temp_files:
            if os.path.exists(temp_file):
                os.unlink(temp_file)

    def create_test_csv(self, data):
        """Helper to create test CSV files"""
        temp_file = tempfile.NamedTemporaryFile(
            mode="w", delete=False, suffix=".csv"
        )
        self.temp_files.append(temp_file.name)

        fieldnames = [
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

        writer = csv.DictWriter(temp_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
        temp_file.close()

        return temp_file.name

    def test_full_integration_flow(self):
        """Test complete integration flow using unittest assertions"""
        test_data = [
            {
                "tracking_number": "TN001",
                "carrier": "DHL",
                "sender_address": "123 Test St",
                "receiver_address": "456 Test Ave",
                "status": "in_transit",
                "article_name": "Test Product",
                "article_quantity": "2",
                "article_price": "29.99",
                "SKU": "SKU001",
            }
        ]

        csv_file = self.create_test_csv(test_data)

        result = load_seed_data_task.apply(args=[csv_file])
        task_result = result.result

        self.assertTrue(task_result["success"])
        self.assertEqual(task_result["total_rows"], 1)
        self.assertEqual(task_result["shipments_created"], 1)
        self.assertEqual(task_result["articles_created"], 1)

        self.assertEqual(Shipment.objects.count(), 1)
        self.assertEqual(Article.objects.count(), 1)

        shipment = Shipment.objects.first()
        self.assertEqual(shipment.tracking_number, "TN001")
        self.assertEqual(shipment.carrier, "DHL")
