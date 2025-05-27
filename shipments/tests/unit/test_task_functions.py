import pytest

from shipments.models import Article, Shipment
from shipments.tasks import process_batch, process_csv_row, validate_csv_file


@pytest.mark.unit
class TestCsvValidation:

    def test_validate_existing_csv_file(self, temp_csv_file):
        """Test validation of a valid CSV file"""
        is_valid, error_message, columns = validate_csv_file(temp_csv_file)

        assert is_valid == True
        assert error_message is None
        assert len(columns) == 9

    def test_validate_nonexistent_file(self):
        """Test validation of non-existent file"""
        is_valid, error_message, columns = validate_csv_file("nonexistent.csv")

        assert is_valid == False
        assert "CSV file not found" in error_message
        assert len(columns) == 9

    def test_validate_csv_missing_columns(self, invalid_csv_file):
        """Test validation of CSV with missing columns"""
        is_valid, error_message, columns = validate_csv_file(invalid_csv_file)

        assert is_valid == False
        assert "Missing required columns" in error_message
        assert "sender_address" in error_message


@pytest.mark.unit
@pytest.mark.django_db
class TestRowProcessing:

    def test_process_valid_row(self):
        """Test processing a valid CSV row"""
        row = {
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

        shipment_created, article_created, error = process_csv_row(row, 1)

        assert shipment_created == True
        assert article_created == True
        assert error is None

        # Verify database objects were created
        assert Shipment.objects.filter(tracking_number="TN001").exists()
        assert Article.objects.filter(sku="SKU001").exists()

    def test_process_duplicate_row(self):
        """Test processing a row with existing tracking number"""
        Shipment.objects.create(
            tracking_number="TN001",
            carrier="DHL",
            sender_address="123 Test St",
            receiver_address="456 Test Ave",
            status="in_transit",
        )

        row = {
            "tracking_number": "TN001",
            "carrier": "FedEx",
            "sender_address": "123 Test St",
            "receiver_address": "456 Test Ave",
            "status": "delivered",
            "article_name": "Test Product",
            "article_quantity": "2",
            "article_price": "29.99",
            "SKU": "SKU001",
        }

        shipment_created, article_created, error = process_csv_row(row, 1)

        assert shipment_created == False
        assert article_created == True
        assert error is None

    def test_process_row_invalid_data(self):
        """Test processing row with invalid numeric data"""
        row = {
            "tracking_number": "TN001",
            "carrier": "DHL",
            "sender_address": "123 Test St",
            "receiver_address": "456 Test Ave",
            "status": "in_transit",
            "article_name": "Test Product",
            "article_quantity": "invalid",
            "article_price": "29.99",
            "SKU": "SKU001",
        }

        shipment_created, article_created, error = process_csv_row(row, 1)

        assert shipment_created == False
        assert article_created == False
        assert error is not None
        assert "Invalid data" in error

    def test_process_row_empty_tracking_number(self):
        """Test processing row with empty tracking number"""
        row = {
            "tracking_number": "",
            "carrier": "DHL",
            "sender_address": "123 Test St",
            "receiver_address": "456 Test Ave",
            "status": "in_transit",
            "article_name": "Test Product",
            "article_quantity": "2",
            "article_price": "29.99",
            "SKU": "SKU001",
        }

        shipment_created, article_created, error = process_csv_row(row, 1)

        assert shipment_created == False
        assert article_created == False
        assert error is not None
        assert "Empty tracking number" in error


@pytest.mark.unit
@pytest.mark.django_db
class TestBatchProcessing:
    """UNIT TEST: Test batch processing logic"""

    def test_process_valid_batch(self, sample_csv_data):
        """Test processing a valid batch of rows"""
        shipments_created, articles_created, errors = process_batch(
            sample_csv_data, 0
        )

        assert shipments_created == 2
        assert articles_created == 2
        assert len(errors) == 0

        # Verify database objects
        assert Shipment.objects.count() == 2
        assert Article.objects.count() == 2

    def test_process_batch_with_errors(self):
        """Test processing batch with some invalid rows"""
        batch_data = [
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
            },
            {
                "tracking_number": "",  # Invalid row
                "carrier": "FedEx",
                "sender_address": "789 Test St",
                "receiver_address": "321 Test Ave",
                "status": "delivered",
                "article_name": "Another Product",
                "article_quantity": "invalid",  # Invalid quantity
                "article_price": "15.50",
                "SKU": "SKU002",
            },
        ]

        shipments_created, articles_created, errors = process_batch(
            batch_data, 0
        )

        assert shipments_created == 1
        assert articles_created == 1
        assert len(errors) == 1
        assert "Empty tracking number" in errors[0]

    def test_process_empty_batch(self):
        """Test processing an empty batch"""
        shipments_created, articles_created, errors = process_batch([], 0)

        assert shipments_created == 0
        assert articles_created == 0
        assert len(errors) == 0
