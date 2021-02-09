from django.db import models, transaction
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
        related_name="SensorType",
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



# TODO: these are not needed here.
def save_measurement(datasource, key, measurement, time):
    try:
        channel = datasource.channels.get(uniquename=key)
    except Channel.DoesNotExist:
        print(
            f"Channel {key} not found for datasource {datasource.name}, creating channel {key}"
        )
        channel = Channel.objects.create(datasource=datasource, uniquename=key)
    print(f"Creating value {measurement[key]} to channel {channel.uniquename}")
    Value.objects.create(channel=channel, time=time, value=measurement[key])


@transaction.atomic
def save_data(message):
    # get the data source type and data source
    devid = message["meta"]["dev-id"]
    datasourcetype = Datasourcetype.objects.get(name=message["meta"]["dev-type"])
    try:
        datasource = datasourcetype.datasources.get(devid=devid)
    except Datasource.DoesNotExist:
        print(f"Creating new datasource {devid}")
        datasource = Datasource(devid=devid, datasourcetype=datasourcetype)
        datasource.save()
        print("Created new datasource")
    for data in message["data"]:
        time = None
        for items in data:
            if "time" in items:
                # read the time entry for the measurements
                print("Reading time for the measurements")
                time = items["time"]
            elif "measurement" in items:
                # save all the measurements
                print("Reading measurements")
                measurement = items["measurement"]
                for key in measurement:
                    save_measurement(datasource, key, measurement, time)
