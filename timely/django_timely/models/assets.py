from django.db import models


class AssetType(models.Model):
    name = models.CharField(max_length=128)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    @classmethod
    def populate_defaults(cls):
        cls.objects.get_or_create(name="Horses")
        cls.objects.get_or_create(name="Machines")
        cls.objects.get_or_create(name="Saddles")
        cls.objects.get_or_create(name="Bridles")
        cls.objects.get_or_create(name="Clothing")
        cls.objects.get_or_create(name="Grooming")
        cls.objects.get_or_create(name="Training")


class Asset(models.Model):
    name = models.CharField(max_length=128)
    type = models.ForeignKey(AssetType, on_delete=models.RESTRICT)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    @classmethod
    def populate_defaults(cls):
        defaults = {
            "Horses": ["Bella", "Dusty", "Pippin"],
            "Machines": ["Horse walker", "Beamer"],
            "Saddles": ["English saddle", "Western saddle", "Dressage saddle"],
            "Bridles": ["Snaffle", "Double", "Bitless bridle"],
            "Clothing": ["Helmet", "Jacket", "Breeches"],
            "Grooming": ["Comb", "Brush", "Hoof pick"],
            "Training": ["Lunge line", "Cone kit"],
        }
        for _type, _lst in defaults.items():
            asset_type = AssetType.objects.get(name=_type)
            for _name in _lst:
                cls.objects.get_or_create(name=_name, type=asset_type)


class AssetAvailability(models.Model):
    class AvailabilityType(models.TextChoices):
        OPEN = "O", "Open"
        CLOSED = "C", "Closed"

    asset = models.ForeignKey(
        Asset,
        on_delete=models.RESTRICT,
        related_name="availability_slots",
        related_query_name="availability_slot",
        verbose_name="Asset",
        help_text="Asset this availability slot applies to.",
    )
    "Asset this availability slot applies to."

    type = models.CharField(
        verbose_name="Availability type",
        choices=AvailabilityType,
        help_text="Type of availability slot (e.g., open, maintenance, reserved).",
    )
    "Type of availability slot (e.g., open, maintenance, reserved)."

    data = models.TextField(
        verbose_name="Recurrence rule",
        help_text="Recurrence rule in iCalendar `RFC 5545` format.",
    )
    "Recurrence rule in iCalendar `RFC 5545` format."


class AssetGroup(models.Model):
    name = models.CharField(max_length=100)
    assets = models.ManyToManyField(Asset, related_name="asset_groups")

    def __str__(self):
        return self.name


class Venue(models.Model):
    name = models.CharField(max_length=128)
    location = models.CharField(max_length=128)
    assets = models.ManyToManyField(
        Asset,
        blank=True,
        help_text="Fixed assets located at this venue",
    )

    def __str__(self):
        return self.name

    @classmethod
    def populate_defaults(cls):
        cls.objects.get_or_create(name="Main arena", location="Stables")
        cls.objects.get_or_create(name="Small arena", location="Stables")
        cls.objects.get_or_create(name="Round arena", location="Stables")
