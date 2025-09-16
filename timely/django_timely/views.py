from django.shortcuts import render
import json


# Create your views here.
def home(request):
    business_hours = [
        {"daysOfWeek": [1, 2, 3], "startTime": "08:00", "endTime": "18:00"},
        {"daysOfWeek": [4, 5], "startTime": "10:00", "endTime": "16:00"},
    ]
    return render(
        request,
        "django_timely/base.html",
        {"business_hours": json.dumps(business_hours)},
    )
