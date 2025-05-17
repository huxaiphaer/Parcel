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
