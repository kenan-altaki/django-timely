from django.contrib import admin

from .models import (
    Availability,
    Event,
    EventParticipant,
    EventParticipantResource,
    EventType,
    ResourceGroup,
    Resource,
    ResourceType,
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
    list_display = ["name", "type", *EVENT_BASE_LIST_DISPLAY]


@admin.register(ResourceType)
class ResourceTypeAdmin(admin.ModelAdmin):
    list_display = ["name", "is_active"]


class AvailabilityInline(admin.StackedInline):
    model = Availability
    extra = 0
    list_display = ["start_time", "end_time"]


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ["name", "type", "is_active"]
    inlines = [
        AvailabilityInline,
    ]
    inlines[0].fields = ["recurrence_rule", "start_time", "end_time"]


@admin.register(ResourceGroup)
class ResourceGroupAdmin(admin.ModelAdmin):
    pass


@admin.register(EventParticipant)
class EventParticipantAdmin(admin.ModelAdmin):
    pass


@admin.register(EventParticipantResource)
class EventParticipantResourceAdmin(admin.ModelAdmin):
    pass


