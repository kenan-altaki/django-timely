from django.contrib import admin

# Register your models here.
from .models import (
    AssetType,
    Asset,
    AssetGroup,
    BookingRequest,
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


@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ["name", "type", "is_active"]


@admin.register(AssetGroup)
class AssetGroupAdmin(admin.ModelAdmin):
    pass


@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    pass


@admin.register(BookingRequest)
class BookingRequestAdmin(admin.ModelAdmin):
    pass


@admin.register(EventParticipant)
class EventParticipantAdmin(admin.ModelAdmin):
    pass


@admin.register(EventParticipantAsset)
class EventParticipantAssetAdmin(admin.ModelAdmin):
    pass
