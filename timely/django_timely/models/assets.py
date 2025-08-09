from django.db import models


class Asset(models.Model):
    name = models.CharField(max_length=128)
    type = models.CharField(max_length=64)
    is_active = models.BooleanField(default=True)


class AssetGroup(models.Model):
    name = models.CharField(max_length=100)
    assets = models.ManyToManyField(Asset, related_name="asset_groups")


class Venue(models.Model):
    name = models.CharField(max_length=128)
    location = models.CharField(max_length=128)
    assets = models.ManyToManyField(
        Asset,
        blank=True,
        help_text="Fixed assets located at this venue",
    )
