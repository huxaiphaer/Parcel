import uuid as uuid

from django.db import models
from django_extensions.db.models import TimeStampedModel
from django_softdelete.models import SoftDeleteModel


class Shipment(TimeStampedModel, SoftDeleteModel):

    class Carrier(models.TextChoices):
        DHL = "DHL"
        UPS = "UPS"
        DPD = "DPD"
        FEDEX = "FedEx"
        GLS = "GLS"

    class Status(models.TextChoices):
        IN_TRANSIT = "in-transit", "In Transit"
        INBOUND_SCAN = "inbound-scan", "Inbound Scan"
        DELIVERY = "delivery", "Delivery"
        TRANSIT = "transit", "Transit"
        SCANNED = "scanned", "Scanned"

    uuid = models.UUIDField(
        unique=True,
        max_length=500,
        default=uuid.uuid4,
        editable=False,
        db_index=True,
        blank=False,
        null=False,
    )
    tracking_number = models.CharField(max_length=50)
    carrier = models.CharField(max_length=10, choices=Carrier.choices)
    sender_address = models.TextField()
    receiver_address = models.TextField()
    status = models.CharField(max_length=20, choices=Status.choices)


class Article(TimeStampedModel, SoftDeleteModel):
    uuid = models.UUIDField(
        unique=True,
        max_length=500,
        default=uuid.uuid4,
        editable=False,
        db_index=True,
        blank=False,
        null=False,
    )
    shipment = models.ForeignKey(
        Shipment, related_name="articles", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=100)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    sku = models.CharField(max_length=50)
