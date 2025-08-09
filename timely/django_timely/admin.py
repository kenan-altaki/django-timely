# Register your models here.
from .models import (
    Asset,
    AssetGroup,
    BookingRequest,
    Event,
    EventParticipant,
    EventParticipantAsset,
    EventType,
    Venue,
)


@admin.register(EventType)
class EventTypeAdmin(admin.ModelAdmin):
    pass


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    pass


@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    pass


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
