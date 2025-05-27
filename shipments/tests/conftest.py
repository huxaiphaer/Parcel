import csv
import os
import tempfile

import pytest
from shipments.models import Shipment, Article

@pytest.fixture
def valid_shipment_with_articles(db):
    shipment = Shipment.objects.create(
        tracking_number="TN12345678",
        carrier="DHL",
        sender_address="Street 1, 10115 Berlin, Germany",
        receiver_address="Street 10, 75001 Paris, France",
        status="in-transit"
    )

    Article.objects.create(
        shipment=shipment,
        name="Laptop",
        quantity=1,
        price=800,
        sku="LP123"
    )
    Article.objects.create(
        shipment=shipment,
        name="Mouse",
        quantity=1,
        price=25,
        sku="MO456"
    )

    return shipment


@pytest.fixture
def valid_shipment_with_articles(db):
    shipment = Shipment.objects.create(
        tracking_number="TN12345678",
        carrier="DHL",
        sender_address="Street 1, 10115 Berlin, Germany",
        receiver_address="Street 10, 75001 Paris, France",
        status="in-transit",
    )
    Article.objects.create(shipment=shipment, name="Laptop", quantity=1, price="800.00", sku="LP123")
    Article.objects.create(shipment=shipment, name="Mouse", quantity=1, price="25.00", sku="MO456")
    return shipment


@pytest.fixture
def shipment_without_articles(db):
    return Shipment.objects.create(
        tracking_number="TN0000",
        carrier="UPS",
        sender_address="Sender St, Berlin, Germany",
        receiver_address="Receiver St, 10001 New York, USA",
        status="in-transit",
    )


@pytest.fixture
def sample_csv_data():
    """Sample CSV data for testing"""
    return [
        {
            'tracking_number': 'TN001',
            'carrier': 'DHL',
            'sender_address': '123 Sender St',
            'receiver_address': '456 Receiver Ave',
            'status': 'in_transit',
            'article_name': 'Test Product',
            'article_quantity': '2',
            'article_price': '29.99',
            'SKU': 'SKU001'
        },
        {
            'tracking_number': 'TN002',
            'carrier': 'FedEx',
            'sender_address': '789 Another St',
            'receiver_address': '321 Different Ave',
            'status': 'delivered',
            'article_name': 'Another Product',
            'article_quantity': '1',
            'article_price': '15.50',
            'SKU': 'SKU002'
        }
    ]


@pytest.fixture
def temp_csv_file(sample_csv_data):
    """Create a temporary CSV file with sample data"""
    temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv')

    fieldnames = [
        'tracking_number', 'carrier', 'sender_address', 'receiver_address',
        'status', 'article_name', 'article_quantity', 'article_price', 'SKU'
    ]

    writer = csv.DictWriter(temp_file, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(sample_csv_data)
    temp_file.close()

    yield temp_file.name

    # Cleanup
    os.unlink(temp_file.name)


@pytest.fixture
def invalid_csv_file():
    """Create a CSV file with missing columns"""
    temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv')

    fieldnames = ['tracking_number', 'carrier']

    writer = csv.DictWriter(temp_file, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerow({'tracking_number': 'TN001', 'carrier': 'DHL'})
    temp_file.close()

    yield temp_file.name

    os.unlink(temp_file.name)


@pytest.fixture
def large_csv_file():
    """Create a larger CSV file for performance testing"""
    temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv')

    fieldnames = [
        'tracking_number', 'carrier', 'sender_address', 'receiver_address',
        'status', 'article_name', 'article_quantity', 'article_price', 'SKU'
    ]

    writer = csv.DictWriter(temp_file, fieldnames=fieldnames)
    writer.writeheader()

    # Create 1000 rows of test data
    for i in range(1000):
        writer.writerow({
            'tracking_number': f'TN{i:04d}',
            'carrier': 'DHL' if i % 2 == 0 else 'FedEx',
            'sender_address': f'{i} Sender St',
            'receiver_address': f'{i} Receiver Ave',
            'status': 'in_transit',
            'article_name': f'Product {i}',
            'article_quantity': str((i % 5) + 1),
            'article_price': str(round(10.0 + (i % 100), 2)),
            'SKU': f'SKU{i:04d}'
        })

    temp_file.close()
    yield temp_file.name
    os.unlink(temp_file.name)
