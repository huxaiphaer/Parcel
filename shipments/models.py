from django.db import models
from django_softdelete.models import SoftDeleteModel
import uuid as uuid
from django_extensions.db.models import TimeStampedModel


class Shipment(TimeStampedModel, SoftDeleteModel):
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
    carrier = models.CharField(max_length=50)
    sender_address = models.TextField()
    receiver_address = models.TextField()
    status = models.CharField(max_length=50)


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
    shipment = models.ForeignKey(Shipment, related_name='articles', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    sku = models.CharField(max_length=50)
