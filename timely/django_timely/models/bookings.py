from django.contrib.auth import get_user_model
from django.db import models

from .assets import Asset
from .events import Event


# class BookingRequest(models.Model):
#     class Status(models.TextChoices):
#         PENDING = "P", "Pending"
#         WAITING = "W", "On waiting list"
#         CONFIRMED = "C", "Confirmed"
#         CANCELLED = "X", "Cancelled"

#     attendant = models.ForeignKey(
#         get_user_model(),
#         on_delete=models.RESTRICT,
#         related_name="booking_requests",
#         related_query_name="booking_request",
#     )
#     event = models.ForeignKey(
#         Event,
#         on_delete=models.RESTRICT,
#         related_name="booking_requests",
#         related_query_name="booking_request",
#     )
#     status = models.CharField(
#         max_length=1,
#         choices=Status,
#     )


class EventParticipant(models.Model):
    class Role(models.TextChoices):
        ATTENDEE = "attendee", "Attendee"
        INSTRUCTOR = "instructor", "Instructor"
        PRESENTER = "presenter", "Presenter"
        FACILITATOR = "facilitator", "Facilitator"
        ASSISTANT = "assistant", "Assistant"

    class Status(models.TextChoices):
        INVITED = "invited", "Invited"
        CONFIRMED = "confirmed", "Confirmed"
        CANCELLED = "cancelled", "Cancelled"

    event = models.ForeignKey(Event, on_delete=models.RESTRICT)
    user = models.ForeignKey(get_user_model(), on_delete=models.RESTRICT)
    role = models.CharField(
        max_length=12,
        choices=Role.choices,
        default=Role.ATTENDEE,
        help_text="The role of this participant in the event",
    )
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.INVITED,
        help_text="The current status of this participant",
    )
    assets = models.ManyToManyField(Asset, through="EventParticipantAsset")

    def __str__(self):
        return f"{self.user} - {self.get_role_display()} for {self.event}"


class EventParticipantAsset(models.Model):
    participant = models.ForeignKey(EventParticipant, on_delete=models.RESTRICT)
    asset = models.ForeignKey(Asset, on_delete=models.RESTRICT)
    shared = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["participant", "asset"], name="unique_participant_asset"
            )
        ]
