from django.db import models
from django.utils.translation import ugettext_lazy as _


class SensorType(models.Model):
    """
    A SensorType is a family of devices, which are parsed using the same parser
    """

    name = models.CharField(
        max_length=100, blank=True, editable=True, verbose_name=_("Name")
    )
    description = models.TextField(
        blank=True, editable=True, verbose_name=_("Description")
    )
    parser = models.CharField(
        max_length=100, blank=True, editable=True, verbose_name=_("Parser")
    )
    created_at = models.DateTimeField(null=False, blank=False, auto_now_add=True)
    updated_at = models.DateTimeField(null=False, blank=False, auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.parser})"


class Device(models.Model):
    """
    A Device is an object, which has unique device id
    """

    sensortype = models.ForeignKey(
        SensorType,
        related_name="sensortype",
        default=None,
        on_delete=models.CASCADE,
    )
    devid = models.CharField(max_length=40, unique=True, db_index=True)
    name = models.CharField(
        max_length=100, blank=True, editable=True, verbose_name=_("Name")
    )
    description = models.TextField(
        blank=True, editable=True, verbose_name=_("Description")
    )
    lat = models.FloatField(
        blank=True, null=True, verbose_name=_("Latitude (dd.ddddd)")
    )
    lon = models.FloatField(
        blank=True, null=True, verbose_name=_("Longitude (dd.ddddd)")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.devid} {self.name}"
