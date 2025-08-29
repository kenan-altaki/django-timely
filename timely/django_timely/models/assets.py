from dataclasses import dataclass

from django.db import models

from django.utils import timezone
from recurrence.fields import RecurrenceField


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

    def get_av_per_month(self, year, month):
        days_in_month = self.det_final_day(year, month)
        dtstart = timezone.datetime(year, month, 1, 0, 0, 0, 0)
        dtend = timezone.datetime(year, month, days_in_month, 23, 59, 59, 999)

        all_occurrences = []
        for each in self.availabilities.all():
            for x in each.recurrence_rule.between(
                dtstart, dtend, dtstart=dtstart, inc=True
            ):
                all_occurrences.append(
                    TimePeriod(
                        start_time=x.replace(
                            hour=each.start_time.hour,
                            minute=each.start_time.minute,
                            second=each.start_time.second,
                        ),
                        end_time=x.replace(
                            hour=each.end_time.hour,
                            minute=each.end_time.minute,
                            second=each.end_time.second,
                        ),
                    )
                )

        all_occurrences.sort(key=lambda x: x.start_time)
        return all_occurrences

    def det_final_day(self, year, month):
        from calendar import monthrange

        return monthrange(year, month)[1]


class AssetAvailability(models.Model):
    asset = models.ForeignKey(
        Asset,
        on_delete=models.RESTRICT,
        related_name="availabilities",
        related_query_name="availability",
    )

    recurrence_rule = RecurrenceField(
        verbose_name="Recurrence rule",
        null=True,
        blank=True,
        help_text="Recurrence rule in iCalendar `RFC 5545` format.",
        include_dtstart=False,
    )

    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return self.asset.name


class AssetGroup(models.Model):
    name = models.CharField(max_length=100)
    assets = models.ManyToManyField(Asset, related_name="asset_groups")

    def __str__(self):
        return self.name


class Venue(models.Model):
    name = models.CharField(max_length=128)
    location = models.CharField(max_length=128, null=True, blank=True)
    assets = models.ManyToManyField(
        Asset,
        blank=True,
        help_text="Fixed assets located at this venue",
    )

    def __str__(self):
        return self.name

    def get_av_per_month(self, year, month):
        days_in_month = self.det_final_day(year, month)
        dtstart = timezone.datetime(year, month, 1, 0, 0, 0, 0)
        dtend = timezone.datetime(year, month, days_in_month, 23, 59, 59, 999)

        all_occurrences = []
        for each in self.availabilities.all():
            for x in each.recurrence_rule.between(
                dtstart, dtend, dtstart=dtstart, inc=True
            ):
                all_occurrences.append(
                    TimePeriod(
                        start_time=x.replace(
                            hour=each.start_time.hour,
                            minute=each.start_time.minute,
                            second=each.start_time.second,
                        ),
                        end_time=x.replace(
                            hour=each.end_time.hour,
                            minute=each.end_time.minute,
                            second=each.end_time.second,
                        ),
                    )
                )

        all_occurrences.sort(key=lambda x: x.start_time)
        return all_occurrences

    def det_final_day(self, year, month):
        from calendar import monthrange

        return monthrange(year, month)[1]


class VenueAvailability(models.Model):
    venue = models.ForeignKey(
        Venue,
        on_delete=models.RESTRICT,
        related_name="availabilities",
        related_query_name="availability",
    )

    recurrence_rule = RecurrenceField(
        verbose_name="Recurrence rule",
        null=True,
        blank=True,
        help_text="Recurrence rule in iCalendar `RFC 5545` format.",
        include_dtstart=False,
    )

    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return self.venue.name


@dataclass
class TimePeriod:
    start_time: timezone.datetime
    end_time: timezone.datetime

    def __str__(self):
        return f"{self.start_time} ==> {self.end_time}"

    def __repr__(self):
        return f"{self.start_time} ==> {self.end_time}"
