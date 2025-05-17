import pytest
from django.urls import reverse
from rest_framework.test import APIClient


@pytest.mark.django_db
class TestShipmentDetailView:
    def setup_method(self):
        self.client = APIClient()

    def test_shipment_detail_success(self, valid_shipment_with_articles):
        shipment = valid_shipment_with_articles
        url = reverse("v1:shipments", kwargs={
            "tracking_number": shipment.tracking_number,
            "carrier": shipment.carrier
        })

        response = self.client.get(url)

        assert response.status_code == 200
        assert response.data["tracking_number"] == shipment.tracking_number
        assert "articles" in response.data
        assert len(response.data["articles"]) == shipment.articles.count()

    def test_shipment_not_found_invalid_tracking(self, valid_shipment_with_articles):
        shipment = valid_shipment_with_articles
        url = reverse("v1:shipments", kwargs={
            "tracking_number": "INVALID123",
            "carrier": shipment.carrier
        })

        response = self.client.get(url)

        assert response.status_code == 404
        assert response.data["error"] == "Shipment not found"

    def test_shipment_not_found_invalid_carrier(self, valid_shipment_with_articles):
        shipment = valid_shipment_with_articles
        url = reverse("v1:shipments", kwargs={
            "tracking_number": shipment.tracking_number,
            "carrier": "FAKECARRIER"
        })

        response = self.client.get(url)

        assert response.status_code == 404
        assert response.data["error"] == "Shipment not found"

    def test_shipment_with_no_articles(self, shipment_without_articles):
        shipment = shipment_without_articles
        url = reverse("v1:shipments", kwargs={
            "tracking_number": shipment.tracking_number,
            "carrier": shipment.carrier
        })

        response = self.client.get(url)

        assert response.status_code == 200
        assert response.data["tracking_number"] == shipment.tracking_number
        assert "articles" in response.data
        assert len(response.data["articles"]) == 0
