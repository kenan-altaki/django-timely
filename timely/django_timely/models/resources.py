from pydantic import BaseModel

from recurrence.fields import RecurrenceField

from django.db import models
from django.utils import timezone


class TimePeriod(BaseModel):
    start: timezone.datetime
    end: timezone.datetime

    def flatten(self, entry_list, reversed=False):
        step = -1 if reversed else 1
        result = []
        for each in entry_list:
            result.append((each.start, step))
            result.append((each.end, -step))
        return result

    def __str__(self):
        return f"{self.start} ==> {self.end}"


class ResourceType(models.Model):
    name = models.CharField(max_length=128)
    is_active = models.BooleanField(default=True)


class Resource(models.Model):
    name = models.CharField(max_length=128)
    is_active = models.BooleanField(default=True)
    type = models.ForeignKey(ResourceType, on_delete=models.RESTRICT)

    def get_availability_for_time(
        self, dtstart: timezone.datetime, dtend: timezone.datetime
    ):
        assert dtstart.tzinfo is not None or dtend.tzinfo is not None, (
            "`dtstart` and `dtend` must have a valid timezone info."
        )
        total_availability = self.get_availability_for_period(
            dtstart=dtstart, dtend=dtend
        )
        availability_flat_list = []
        for availability in total_availability:
            availability_flat_list.append((availability.start, 1))
            availability_flat_list.append((availability.end, -1))

        all_events = self.events.filter(start__gte=dtstart, start__lte=dtend)
        for reservation in all_events:
            availability_flat_list.append((reservation.start, -1))
            availability_flat_list.append((reservation.end, 1))

        availability_flat_list.sort(key=lambda x: (x[0], -x[1]))

        counter = 0
        counter_history = 0
        final_list = []

        _start_time, _end_time = None, None
        for instance, step in availability_flat_list:
            counter += step
            if counter_history == 0 and counter > 0:
                _start_time = instance
            if counter_history > 0 and counter == 0:
                _end_time = instance
                if _end_time == _start_time:
                    _start_time, _end_time = None, None
                    continue
                final_list.append(
                    TimePeriod(start_time=_start_time, end_time=_end_time)
                )
                _start_time, _end_time = None, None
            if counter < 0 or counter_history < 0:
                print("Error, counter should not go below 0.")
            counter_history = counter

        return final_list

    def get_availabilities_per_month(self, year: int, month: int):
        days_in_month = self.get_final_day_in_month(year, month)
        dtstart = timezone.datetime(year, month, 1, 0, 0, 0, 0)
        dtend = timezone.datetime(year, month, days_in_month, 23, 59, 59, 999)

        return self.get_availability_for_period(dtstart, dtend)

    def get_availability_for_period(
        self,
        dtstart: timezone.datetime,
        dtend: timezone.datetime,
    ):
        assert dtstart.tzinfo is not None or dtend.tzinfo is not None, (
            "`dtstart` and `dtend` must have a valid timezone info."
        )

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

    @classmethod
    def get_final_day_in_month(cls, year, month):
        from calendar import monthrange

        return monthrange(year, month)[1]

    def merge_availabilities(self, p_year: int = None, p_month: int = None):
        assert hasattr(self, "availabilities"), (
            f"{self} does not have an `availability` attribute."
        )

        if p_year is None:
            year = timezone.now().year
        else:
            year = p_year

        if p_month is None:
            month = timezone.now().month
        else:
            month = p_month

        availabilities = self.get_availabilities_per_month(year, month)
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
                if _end_time == _start_time:
                    continue
                final_list.append(
                    TimePeriod(start_time=_start_time, end_time=_end_time)
                )
                _start_time, _end_time = None, None
            if counter < 0 or counter_history < 0:
                print("Error, counter should not go below 0.")
            counter_history = counter

        # return final_list
        from pprint import pprint

        pprint(final_list)


class ResourceGroup(models.Model):
    name = models.CharField(max_length=100)
    resources = models.ManyToManyField(Resource, related_name="groups")


class Availability(models.Model):
    recurrence_rule = RecurrenceField(
        verbose_name="Recurrence rule",
        null=True,
        blank=True,
        help_text="Recurrence rule in iCalendar `RFC 5545` format.",
        include_dtstart=False,
    )

    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    resource = models.ForeignKey(
        Resource,
        on_delete=models.RESTRICT,
        related_name="availabilities",
        related_query_name="availability",
    )

    def __str__(self):
        return (self.start_time, self.end_time)

    @classmethod
    def overlapping_availabilities(
        cls, *items, p_year: int = None, p_month: int = None
    ):
        for item in items:
            assert hasattr(item, "availabilities"), (
                f"{item} does not have an `availability` attribute."
            )

        if p_year is None:
            year = timezone.now().year
        else:
            year = p_year

        if p_month is None:
            month = timezone.now().month
        else:
            month = p_month

        counter = 0
        counter_history = 0
        starting_list = []
        object_list = []
        final_list = []

        for each in items:
            starting_list.extend(each.merge_availabilities(p_year=year, p_month=month))
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
