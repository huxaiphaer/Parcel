import pytest
from shipments.views import ShipmentDetailView

@pytest.mark.django_db
class TestExtractCity:
    def test_standard_address_with_zip(self):
        address = "Street 10, 75001 Paris, France"
        expected = "Paris"
        result = ShipmentDetailView.extract_city(address)
        assert result == expected

    def test_address_without_zip(self):
        address = "Avenue de la République, Paris, France"
        expected = "Paris"
        result = ShipmentDetailView.extract_city(address)
        assert result == expected

    def test_malformed_address(self):
        address = "Unknown format"
        expected = ""
        result = ShipmentDetailView.extract_city(address)
        assert result == expected

    def test_german_address_with_zip(self):
        address = "123 Road, 10000 Berlin, Germany"
        expected = "Berlin"
        result = ShipmentDetailView.extract_city(address)
        assert result == expected
