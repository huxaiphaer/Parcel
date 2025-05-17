from django.urls import path

from shipments.views import ShipmentDetailView

urlpatterns = [

    path("shipments/<str:tracking_number>/<str:carrier>/", ShipmentDetailView.as_view(), name="shipments"),
]
