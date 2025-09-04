from django.contrib import admin
from django.forms import HiddenInput

from .models import (
    Asset,
    AssetGroup,
    Availability,
    AssetType,
    Event,
    EventParticipant,
    EventParticipantAsset,
    EventType,
    Venue,
)

EVENT_BASE_LIST_DISPLAY = [
    "requires_confirmation",
    "allows_waitlist",
    "max_capacity",
    "booking_policy",
    "access_level",
    "is_active",
]


@admin.register(EventType)
class EventTypeAdmin(admin.ModelAdmin):
    list_display = ["name", *EVENT_BASE_LIST_DISPLAY]


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ["name", "type", "venue", *EVENT_BASE_LIST_DISPLAY]


@admin.register(AssetType)
class AssetTypeAdmin(admin.ModelAdmin):
    list_display = ["name", "is_active"]


class AvailabilityInline(admin.StackedInline):
    model = Availability
    extra = 0
    list_display = ["start_time", "end_time"]

    # def __init__(self, *args, **kwargs):
    #     super(AvailabilityInline, self).__init__(*args, **kwargs)
    #     if self.model.venue is not None:
    #         self.fields["Asset"].widget = HiddenInput()


@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ["name", "type", "is_active"]
    inlines = [
        AvailabilityInline,
    ]
    inlines[0].fields = ["recurrence_rule", "start_time", "end_time"]


@admin.register(AssetGroup)
class AssetGroupAdmin(admin.ModelAdmin):
    pass


@admin.register(EventParticipant)
class EventParticipantAdmin(admin.ModelAdmin):
    pass


@admin.register(EventParticipantAsset)
class EventParticipantAssetAdmin(admin.ModelAdmin):
    pass


@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    inlines = [
        AvailabilityInline,
    ]
    inlines[0].fields = ["recurrence_rule", "start_time", "end_time"]
