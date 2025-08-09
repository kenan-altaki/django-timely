from django.contrib.auth import get_user_model
from django.db import models

from .assets import Asset
from .events import Event


class BookingRequest(models.Model):
    class Status(models.TextChoices):
        PENDING = "P", "Pending"
        WAITING = "W", "On waiting list"
        CONFIRMED = "C", "Confirmed"
        CANCELLED = "X", "Cancelled"

    attendant = models.ForeignKey(
        get_user_model(),
        on_delete=models.RESTRICT,
        related_name="booking_requests",
        related_query_name="booking_request",
    )
    event = models.ForeignKey(
        Event,
        on_delete=models.RESTRICT,
        related_name="booking_requests",
        related_query_name="booking_request",
    )
    status = models.CharField(
        max_length=1,
        choices=Status,
    )


class EventParticipant(models.Model):
    event = models.ForeignKey(Event, on_delete=models.RESTRICT)
    user = models.ForeignKey(get_user_model(), on_delete=models.RESTRICT)
    role = models.CharField(
        choices=[("compulsory", "Compulsory"), ("optional", "Optional")]
    )
    status = models.CharField(
        choices=[
            ("invited", "Invited"),
            ("confirmed", "Confirmed"),
            ("cancelled", "Cancelled"),
        ]
    )


class EventParticipantAsset(models.Model):
    event = models.ForeignKey(Event, on_delete=models.RESTRICT)
    user = models.ForeignKey(get_user_model(), on_delete=models.RESTRICT)
    asset = models.ForeignKey(Asset, on_delete=models.RESTRICT)
    is_shared = models.BooleanField(default=False)
