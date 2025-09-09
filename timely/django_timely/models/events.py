from recurrence.fields import RecurrenceField

from django.core.exceptions import PermissionDenied
from django.db import models
from django.utils import timezone

from .resources import Resource


class EventBase(models.Model):
    """
    Abstract base model for event-related data, providing common fields and enumerations
    for event booking and access policies.

    Attributes:
        requires_confirmation (bool): Indicates if bookings require manual confirmation.
        allows_waitlist (bool): Allows users to join a waitlist if the event is full.
        rrule_string (str): Recurrence rule in iCalendar RFC 5545 format.
        buffer_before (timedelta): Time buffer before the event starts
            (e.g., for setup).
        buffer_after (timedelta): Time buffer after the event ends (e.g., for cleanup).
        max_capacity (int): Maximum number of participants allowed for the event.
        booking_policy (str): Policy for booking this event. Choices are defined in
            `EventBookingPolicy`.
        access_level (str): Access level required to join the event. Choices are defined
            in `EventAccessLevel`.
    """

    class EventBookingPolicy(models.TextChoices):
        "EventBookingPolicy (TextChoices): Enum for booking policy options."

        FREE = "F", "Free"
        DEPOSIT = "D", "Deposit required"
        PREPAID = "P", "Paid in full"
        POSTPAID = "C", "Paid on credit"

    class EventAccessLevel(models.TextChoices):
        "EventAccessLevel (TextChoices): Enum for event access level options."

        PUBLIC = "P", "Public access"
        RESTRICTED = "R", "Restricted access"
        INVITE = "I", "Invite only"

    requires_confirmation = models.BooleanField(
        verbose_name="Require confirmation",
        default=False,
        help_text="Whether bookings require manual confirmation.",
    )
    "Whether bookings require manual confirmation."

    allows_waitlist = models.BooleanField(
        verbose_name="Allow waitlists",
        default=False,
        help_text="Allow users to join a waitlist if the event is full.",
    )
    "Allow users to join a waitlist if the event is full."

    recurrence_rule = RecurrenceField(
        verbose_name="Recurrence rule",
        null=True,
        blank=True,
        help_text="Recurrence rule in iCalendar `RFC 5545` format.",
    )
    "Recurrence rule in iCalendar `RFC 5545` format."

    buffer_before = models.DurationField(
        verbose_name="Buffer time before event",
        default=timezone.timedelta(minutes=0),
        help_text="Time buffer before the event starts (e.g., for setup).",
        null=True,
        blank=True,
    )
    "Time buffer before the event starts (e.g., for setup)."

    buffer_after = models.DurationField(
        verbose_name="Buffer time after event",
        default=timezone.timedelta(minutes=5),
        help_text="Time buffer after the event ends (e.g., for cleanup).",
        null=True,
        blank=True,
    )
    "Time buffer after the event ends (e.g., for cleanup)."

    max_capacity = models.PositiveIntegerField(
        verbose_name="Maximum capacity",
        default=10,
        help_text="Maximum number of participants allowed for the event.",
    )
    "Maximum number of participants allowed for the event."

    booking_policy = models.CharField(
        verbose_name="Booking policy",
        max_length=1,
        choices=EventBookingPolicy,
        default=EventBookingPolicy.FREE,
        help_text=(
            "Policy for booking this event: Free, Deposit required, or Paid in full."
        ),
    )
    "Policy for booking this event. Choices are defined in `EventBookingPolicy`"

    deposit = models.FloatField(
        verbose_name="Deposit amount",
        null=True,
        blank=True,
        help_text=(
            "The deposit amount required to reserve a spot for this event, if "
            "applicable."
        ),
    )
    "The deposit amount required to reserve a spot for this event, if applicable."

    price = models.FloatField(
        verbose_name="Event price",
        null=True,
        blank=True,
        help_text="The price for the event, if applicable.",
    )
    "The price for the event, if applicable."

    refundable = models.BooleanField(
        verbose_name="Refundable",
        default=True,
        help_text=(
            "Indicates whether payments (such as deposits or fees) are refundable if "
            "the booking is cancelled."
        ),
    )
    """Indicates whether payments (such as deposits or fees) are refundable if the
    booking is cancelled."""

    refundable_before = models.DateTimeField(
        verbose_name="Refundable before",
        null=True,
        blank=True,
        help_text=(
            "The date and time before which a refund is allowed if the booking is "
            "cancelled."
        ),
    )
    "The date and time before which a refund is allowed if the booking is cancelled."

    access_level = models.CharField(
        verbose_name="Access level",
        max_length=1,
        choices=EventAccessLevel,
        default=EventAccessLevel.PUBLIC,
        help_text=(
            "Access level required to join the event: Public, Restricted, or Invite "
            "only."
        ),
    )
    "Access level required to join the event. Choices are defined in `EventAccessLevel`"

    is_active = models.BooleanField(
        verbose_name="Is active",
        default=True,
        help_text="Check if the event should be visible and available for booking.",
    )
    "Indicates whether this event should be visible and available for booking."

    class Meta:
        abstract = True


class EventType(EventBase):
    "Represents a type of event in the system."

    name = models.CharField(
        "Event type name",
        max_length=128,
        help_text="The name of the event type.",
    )
    "The name of the event type."

    def __str__(self):
        return self.name

    @classmethod
    def populate_defaults(cls):
        cls.objects.get_or_create(name="Open slot")
        cls.objects.get_or_create(
            name="Reserved slot",
            requires_confirmation=True,
            booking_policy=cls.EventBookingPolicy.FREE,
            access_level=cls.EventAccessLevel.RESTRICTED,
        )


class Event(EventBase):
    "Represents an event in the system"

    name = models.CharField(
        verbose_name="Event name",
        max_length=128,
        help_text="Enter the descriptive name for this event.",
    )
    "The name of the event."

    type = models.ForeignKey(
        EventType,
        on_delete=models.RESTRICT,
        related_name="events",
        related_query_name="event",
        null=True,
        blank=True,
        verbose_name="Event type",
        help_text="Select the type or category that best describes this event.",
    )
    "The type or category of the event."

    is_locked = models.BooleanField(
        verbose_name="Is locked",
        default=False,
        help_text="If checked, prevents any further changes to this event.",
    )
    "If True, prevents any further changes to this event."

    start = models.DateTimeField(
        verbose_name="Event start date and time",
        help_text="Specify the date and time when the event will begin.",
    )
    "The date and time when the event will begin."

    end = models.DateTimeField(
        verbose_name="Event end date and time",
        help_text="Specify the date and time when the event will end.",
    )
    "The date and time when the event will end."

    resource = models.ManyToManyField(
        Resource,
        help_text="The resources used for this event.",
        through="EventResource",
        related_name="events",
        related_query_name="event",
    )
    "The resources used for this event."

    def __str__(self):
        return f"{self.name}: {self.start} -> {self.end}"

    def save(self, *args, **kwargs):
        if self.is_locked:
            raise PermissionDenied("Cannot save a locked event")

        return super().save(*args, **kwargs)

    @property
    def presenters(self):
        """Get all users with presenter role for this event."""
        from .bookings import EventParticipant

        return EventParticipant.objects.filter(
            event=self, role=EventParticipant.Role.PRESENTER
        )

    @property
    def instructors(self):
        """Get all users with instructor role for this event."""
        from .bookings import EventParticipant

        return EventParticipant.objects.filter(
            event=self, role=EventParticipant.Role.INSTRUCTOR
        )

    @property
    def primary_presenter(self):
        """Get the first confirmed presenter for this event."""
        presenter = self.presenters.filter(status="confirmed").first()
        return presenter.user if presenter else None

    @classmethod
    def populate_defaults(cls):
        open_slots = EventType.objects.get(name="Open slot")
        reserved_slots = EventType.objects.get(name="Reserved slot")
        defaults = [
            {
                "name": "Monday open slots",
                "type": open_slots,
                "start": timezone.now(),
                "end": timezone.now() + timezone.timedelta(hours=1),
            },
            {
                "name": "Monday reserved slots",
                "type": reserved_slots,
                "access_level": cls.EventAccessLevel.RESTRICTED,
                "start": timezone.now() + timezone.timedelta(hours=1),
                "end": timezone.now() + timezone.timedelta(hours=2),
            },
        ]

        objs = [cls(**kwargs) for kwargs in defaults]
        cls.objects.bulk_create(objs, ignore_conflicts=True)


class EventResource(models.Model):
    event = models.ForeignKey(Event, on_delete=models.RESTRICT)
    resource = models.ForeignKey(Resource, on_delete=models.RESTRICT)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["event", "resource"], name="unique_event_resource"
            )
        ]
