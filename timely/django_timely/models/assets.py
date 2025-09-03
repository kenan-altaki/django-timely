from dataclasses import dataclass

from recurrence.fields import RecurrenceField

from django.db import models
from django.utils import timezone


@dataclass
class TimePeriod:
    start_time: timezone.datetime
    end_time: timezone.datetime

    def __str__(self):
        return f"{self.start_time} ==> {self.end_time}"

    def __repr__(self):
        return f"{self.start_time} ==> {self.end_time}"

    # def split_data(self):
    #     return [(self.start_time, "+"), (self.end_time, "-")]


class Availability(models.Model):
    recurrence_rule = RecurrenceField(
        verbose_name="Recurrence rule",
        null=True,
        blank=True,
        help_text="Recurrence rule in iCalendar `RFC 5545` format.",
        include_dtstart=False,
    )

    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        abstract = True

    @classmethod
    def get_av_per_month(cls, year, month):
        days_in_month = cls.det_final_day(year, month)
        dtstart = timezone.datetime(year, month, 1, 0, 0, 0, 0)
        dtend = timezone.datetime(year, month, days_in_month, 23, 59, 59, 999)

        all_occurrences = []
        for each in cls.availabilities.all():
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

    @classmethod
    def det_final_day(cls, year, month):
        from calendar import monthrange

        return monthrange(year, month)[1]

    @classmethod
    def overlap_helper_function(cls, period1: "Availability", period2: "Availability"):
        if (
            (period1.start_time < period2.end_time)
            and (period1.start_time > period2.start_time)
        ) or (
            (period1.end_time < period2.end_time)
            and (period1.end_time > period2.start_time)
        ):
            return 0  # Overlap detected, continue as normal
        elif period1.start_time > period2.end_time:
            return 1  # Period 2 ends before Period 1 starts, skip and move on to next iteration
        elif period1.end_time < period2.start_time:
            return 2  # Period 1 ends before Period 2 starts, ignore all future iterations and break loop

    @classmethod
    def overlap_return(cls, a: "Availability", b: "Availability"):
        return max(a.start_time, b.start_time), min(a.end_time, b.end_time)

    @classmethod
    def AND_Overlap(cls, *items, year, month):
        for item in items:
            assert hasattr(item, "availabilities"), (
                f"{item} does not have an `availability` attribute."
            )
        counter = 0
        counter_history = 0
        starting_list = []
        object_list = []
        final_list = []

        for each in items:
            starting_list.extend(cls.OR_Overlap(each, year, month))
        for obj in starting_list:
            assert isinstance(obj, TimePeriod)
            object_list.append((obj.start_time, 1))
            object_list.append((obj.end_time, -1))

        object_list.sort(key=lambda x: x[0])
        list_length = len(items)

        for instance, step in object_list:
            counter += step
            if counter_history < list_length and counter == list_length:
                _start_time = instance
            if counter_history == list_length and counter < list_length:
                _end_time = instance
                final_list.append(
                    TimePeriod(start_time=_start_time, end_time=_end_time)
                )
                _start_time, _end_time = None, None
            if counter < 0 or counter_history < 0:
                print("Error, counter should not go below 0.")
            counter_history = counter

        return final_list

    @classmethod
    def OR_Overlap(cls, item: "Venue", year: int, month: int):
        assert hasattr(item, "availabilities"), (
            f"{item} does not have an `availability` attribute."
        )
        availabilities = item.get_av_per_month(year, month)
        counter = 0
        counter_history = 0

        starting_list: list[tuple[timezone.datetime, int]] = []
        for availability in availabilities:
            assert isinstance(availability, TimePeriod)
            starting_list.append((availability.start_time, 1))
            starting_list.append((availability.end_time, -1))

        starting_list.sort(key=lambda x: x[0])
        final_list: list[TimePeriod] = []

        _start_time, _end_time = None, None
        for instance, step in starting_list:
            counter += step
            if counter_history == 0 and counter > 0:
                _start_time = instance
            if counter_history > 0 and counter == 0:
                _end_time = instance
                final_list.append(
                    TimePeriod(start_time=_start_time, end_time=_end_time)
                )
                _start_time, _end_time = None, None
            if counter < 0 or counter_history < 0:
                print("Error, counter should not go below 0.")
            counter_history = counter

        # from pprint import pprint

        # pprint(final_list)
        return final_list

    @classmethod
    def availability_overlap(cls, *items):
        for item in items:
            assert hasattr(item, "availabilities"), (
                f"{item} does not have an `availability` attribute."
            )

        # Get availability for each item
        item_list_length = len(items)
        assert item_list_length > 1, (
            "You need at least two objects."
        )  # Asserted that item list has more than 1 object

        new_list = []

        temp_start_time = models.TimeField()
        temp_end_time = models.TimeField()
        temp_avail_obj = Availability.objects.new()

        # Determine the overlap of all items
        return new_list


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

    def get_av_per_month(self, year, month):
        days_in_month = self.det_final_day(year, month)
        dtstart = timezone.datetime(year, month, 1, 0, 0, 0, 0)
        dtend = timezone.datetime(year, month, days_in_month, 23, 59, 59, 999)

        all_occurrences: list[TimePeriod] = []
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


class AssetAvailability(Availability):
    asset = models.ForeignKey(
        Asset,
        on_delete=models.RESTRICT,
        related_name="availabilities",
        related_query_name="availability",
    )

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

    def get_av_per_month(self, year, month):
        days_in_month = self.det_final_day(year, month)
        dtstart = timezone.datetime(year, month, 1, 0, 0, 0, 0)
        dtend = timezone.datetime(year, month, days_in_month, 23, 59, 59, 999)

        all_occurrences: list[TimePeriod] = []
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

    def __str__(self):
        return self.name


class VenueAvailability(Availability):
    venue = models.ForeignKey(
        Venue,
        on_delete=models.RESTRICT,
        related_name="availabilities",
        related_query_name="availability",
    )

    def __str__(self):
        return self.venue.name
