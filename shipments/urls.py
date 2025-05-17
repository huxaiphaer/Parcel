from django.urls import path

from shipments.views import ShipmentDetailView

urlpatterns = [

    path("shipments/", ShipmentDetailView.as_view(), name="shipments"),
]
