from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Shipment
from .serializers import ShipmentSerializer
from .services import get_weather


class ShipmentDetailView(APIView):

    """Shipment Detail View."""

    def get(self, request, tracking_number, carrier):
        try:
            shipment = Shipment.objects.prefetch_related('articles').filter(
                tracking_number=tracking_number, carrier=carrier
            ).first()
            data = ShipmentSerializer(shipment).data
            city = shipment.receiver_address.split(",")[-2].strip()
            data["weather"] = get_weather(city)
            return Response(data)
        except Exception as ex:
            raise ex
