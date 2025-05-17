import re

from drf_spectacular.utils import extend_schema
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from weather.services import get_weather
from .models import Shipment
from .serializers import ShipmentSerializer
import logging

logger = logging.getLogger(__name__)


@extend_schema(
    responses={200: ShipmentSerializer}
)
class ShipmentDetailView(APIView):
    """Shipment Detail View."""
    serializer_class = ShipmentSerializer

    @staticmethod
    def extract_city(receiver_address: str) -> str:
        """
        Extracts the city name from a formatted address.
        Assumes city is the second-to-last comma-separated part, and removes numeric tokens like ZIP codes.
        """
        parts = [part.strip() for part in receiver_address.split(",")]

        if len(parts) < 2:
            return ''

        city_with_zip = parts[-2]
        words = city_with_zip.split()

        city = " ".join(word for word in words if not word.isdigit())
        return city

    def get(self, request, tracking_number, carrier):
        try:
            shipment = Shipment.objects.prefetch_related('articles').filter(
                tracking_number=tracking_number, carrier=carrier
            ).first()

            if not shipment:
                return Response({"error": "Shipment not found"}, status=status.HTTP_404_NOT_FOUND)

            data = self.serializer_class(shipment).data
            city = self.extract_city(receiver_address=shipment.receiver_address)

            try:
                data["weather"] = get_weather(city)
            except Exception as weather_ex:
                logger.warning(f"Failed to fetch weather for {city}: {weather_ex}")
                data["weather"] = {"error": "Weather data unavailable"}

            return Response(data)

        except Exception as ex:
            logger.error(f"Unhandled error in ShipmentDetailView: {ex}", exc_info=True)
            return Response({"error": "Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
