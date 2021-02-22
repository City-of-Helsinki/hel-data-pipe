from django.db import models
from django.utils.translation import ugettext_lazy as _

from parser.management.commands import sensor


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
        max_length=100, blank=True, verbose_name=_("Parser"),
        choices=sensor.get_parser_choices()
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


class RAW_MESSAGE_STATUS(models.TextChoices):
    NETWORK_PARSER_NOT_FOUND = 'network-parser-not-found', _('Network parser not found')
    NW_DATA_ERROR =  'nw-data-error', _('Invalid sensor network data')
    DEVICE_ID_NOT_FOUND = 'device-id-not-found', _('Device ID not found')
    PARSER_NOT_FOUND = 'parser-not-found', _('Parser not found')
    PARSER_ERROR = 'parser-error', _('Parsing of hex payload failed')


class RawMessage(models.Model):
    """ A raw HTTP message. Typically stored for reprocessing purposes. """

    created_at = models.DateTimeField(null=False, blank=False, auto_now_add=True)
    updated_at = models.DateTimeField(null=False, blank=False, auto_now=True)
    data = models.BinaryField(blank=True, editable=True, verbose_name=_("Raw data"))
    status =  models.CharField(
        max_length=100, blank=True, choices=RAW_MESSAGE_STATUS.choices)

    # Used only for visualization purpose, (re)processing is done for 'data' field
    json_data = models.JSONField(blank=True, editable=True, verbose_name=_("Raw text converted data"), default=dict)

    # Optional, not always available if parsing fails
    devid = models.CharField(max_length=40)
