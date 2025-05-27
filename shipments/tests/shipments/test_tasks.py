import os
import csv
import tempfile
import pytest
from unittest.mock import patch, MagicMock
from django.test import TransactionTestCase

from shipments.models import Shipment, Article
from shipments.tasks import load_seed_data_task



@pytest.mark.integration
@pytest.mark.django_db
class TestCeleryTaskIntegration:

    @patch('shipments.tasks.load_seed_data_task.update_state')
    def test_successful_task_execution(self, mock_update_state, temp_csv_file):
        """Test successful execution of the full task end-to-end"""
        # Mock the task instance
        mock_task = MagicMock()
        mock_task.update_state = mock_update_state

        result = load_seed_data_task(mock_task, temp_csv_file, batch_size=1)

        # Verify task results
        assert result['success'] == True
        assert result['total_rows'] == 2
        assert result['shipments_created'] == 2
        assert result['articles_created'] == 2
        assert result['errors'] == 0

        # Verify progress tracking was called
        assert mock_update_state.called

        # Verify database state
        assert Shipment.objects.count() == 2
        assert Article.objects.count() == 2

        # Verify specific data was created correctly
        shipment = Shipment.objects.get(tracking_number='TN001')
        assert shipment.carrier == 'DHL'
        assert shipment.status == 'in_transit'

        article = Article.objects.get(sku='SKU001')
        assert article.name == 'Test Product'
        assert article.quantity == 2
        assert article.price == 29.99

    def test_task_with_invalid_file(self):
        """Test task execution with invalid file path"""
        mock_task = MagicMock()

        result = load_seed_data_task(mock_task, 'nonexistent.csv')

        assert result['success'] == False
        assert 'CSV file not found' in result['message']

        # Verify no database objects were created
        assert Shipment.objects.count() == 0
        assert Article.objects.count() == 0

    @patch('shipments.tasks.load_seed_data_task.update_state')
    def test_task_with_large_file(self, mock_update_state, large_csv_file):
        """Test task execution with large file (performance test)"""
        mock_task = MagicMock()
        mock_task.update_state = mock_update_state

        result = load_seed_data_task(mock_task, large_csv_file, batch_size=100)

        # Verify task completed successfully
        assert result['success'] == True
        assert result['total_rows'] == 1000
        assert result['shipments_created'] == 1000
        assert result['articles_created'] == 1000
        assert result['errors'] == 0

        assert mock_update_state.call_count >= 10

        assert Shipment.objects.count() == 1000
        assert Article.objects.count() == 1000

    @patch('shipments.tasks.load_seed_data_task.update_state')
    def test_task_with_mixed_data(self, mock_update_state):
        """Test task with mix of valid and invalid data"""
        temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv')

        fieldnames = [
            'tracking_number', 'carrier', 'sender_address', 'receiver_address',
            'status', 'article_name', 'article_quantity', 'article_price', 'SKU'
        ]

        writer = csv.DictWriter(temp_file, fieldnames=fieldnames)
        writer.writeheader()

        test_data = [
            {  # Valid row
                'tracking_number': 'TN001',
                'carrier': 'DHL',
                'sender_address': '123 Test St',
                'receiver_address': '456 Test Ave',
                'status': 'in_transit',
                'article_name': 'Product 1',
                'article_quantity': '2',
                'article_price': '29.99',
                'SKU': 'SKU001'
            },
            {  # Invalid row - missing tracking number
                'tracking_number': '',
                'carrier': 'FedEx',
                'sender_address': '789 Test St',
                'receiver_address': '321 Test Ave',
                'status': 'delivered',
                'article_name': 'Product 2',
                'article_quantity': '1',
                'article_price': '15.50',
                'SKU': 'SKU002'
            },
            {  # Invalid row - bad quantity
                'tracking_number': 'TN003',
                'carrier': 'UPS',
                'sender_address': '555 Test St',
                'receiver_address': '777 Test Ave',
                'status': 'pending',
                'article_name': 'Product 3',
                'article_quantity': 'invalid',
                'article_price': '25.00',
                'SKU': 'SKU003'
            },
            {  # Valid row
                'tracking_number': 'TN004',
                'carrier': 'USPS',
                'sender_address': '888 Test St',
                'receiver_address': '999 Test Ave',
                'status': 'delivered',
                'article_name': 'Product 4',
                'article_quantity': '3',
                'article_price': '45.00',
                'SKU': 'SKU004'
            }
        ]

        writer.writerows(test_data)
        temp_file.close()

        try:
            mock_task = MagicMock()
            mock_task.update_state = mock_update_state

            result = load_seed_data_task(mock_task, temp_file.name, batch_size=2)

            # Should complete successfully despite errors
            assert result['success'] == True
            assert result['total_rows'] == 4
            assert result['shipments_created'] == 2
            assert result['articles_created'] == 2
            assert result['errors'] == 2

            # Verify only valid data was saved
            assert Shipment.objects.count() == 2
            assert Article.objects.count() == 2

            # Verify specific valid data
            assert Shipment.objects.filter(tracking_number='TN001').exists()
            assert Shipment.objects.filter(tracking_number='TN004').exists()
            assert not Shipment.objects.filter(tracking_number='TN003').exists()

        finally:
            os.unlink(temp_file.name)

    def test_task_with_duplicate_data(self):
        """Test task behavior with duplicate tracking numbers"""
        existing_shipment = Shipment.objects.create(
            tracking_number='TN001',
            carrier='DHL',
            sender_address='Original Address',
            receiver_address='Original Receiver',
            status='pending'
        )

        # Create CSV with duplicate tracking number
        temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv')

        fieldnames = [
            'tracking_number', 'carrier', 'sender_address', 'receiver_address',
            'status', 'article_name', 'article_quantity', 'article_price', 'SKU'
        ]

        writer = csv.DictWriter(temp_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow({
            'tracking_number': 'TN001',
            'carrier': 'FedEx',
            'sender_address': '123 New St',
            'receiver_address': '456 New Ave',
            'status': 'delivered',
            'article_name': 'New Product',
            'article_quantity': '1',
            'article_price': '20.00',
            'SKU': 'SKU001'
        })
        temp_file.close()

        try:
            mock_task = MagicMock()
            result = load_seed_data_task(mock_task, temp_file.name)

            # Should complete successfully
            assert result['success'] == True
            assert result['total_rows'] == 1
            assert result['shipments_created'] == 0
            assert result['articles_created'] == 1

            shipment = Shipment.objects.get(tracking_number='TN001')
            assert shipment.carrier == 'DHL'
            assert shipment.sender_address == 'Original Address'

            assert Article.objects.filter(sku='SKU001').exists()

        finally:
            os.unlink(temp_file.name)


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
        temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv')
        self.temp_files.append(temp_file.name)

        fieldnames = [
            'tracking_number', 'carrier', 'sender_address', 'receiver_address',
            'status', 'article_name', 'article_quantity', 'article_price', 'SKU'
        ]

        writer = csv.DictWriter(temp_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
        temp_file.close()

        return temp_file.name

    def test_full_integration_flow(self):
        """Test complete integration flow using unittest assertions"""
        test_data = [{
            'tracking_number': 'TN001',
            'carrier': 'DHL',
            'sender_address': '123 Test St',
            'receiver_address': '456 Test Ave',
            'status': 'in_transit',
            'article_name': 'Test Product',
            'article_quantity': '2',
            'article_price': '29.99',
            'SKU': 'SKU001'
        }]

        csv_file = self.create_test_csv(test_data)
        mock_task = MagicMock()

        result = load_seed_data_task(mock_task, csv_file)

        self.assertTrue(result['success'])
        self.assertEqual(result['total_rows'], 1)
        self.assertEqual(result['shipments_created'], 1)
        self.assertEqual(result['articles_created'], 1)

        # Verify database state
        self.assertEqual(Shipment.objects.count(), 1)
        self.assertEqual(Article.objects.count(), 1)

        shipment = Shipment.objects.first()
        self.assertEqual(shipment.tracking_number, 'TN001')
        self.assertEqual(shipment.carrier, 'DHL')
