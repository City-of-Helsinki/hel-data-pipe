from django.db import models, transaction
from django.utils.translation import ugettext_lazy as _


class Datasourcetype(models.Model):
    """
    A Datasourcetype is a family of devices, which are parsed using the same parser
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
        return "{} ({})".format(self.name, self.parser)


class Datasource(models.Model):
    """
    A Datasource is an object, which has unique device id
    """

    datasourcetype = models.ForeignKey(
        Datasourcetype,
        related_name="datasources",
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
        return "{} {}".format(self.devid, self.name)


class Quantity(models.Model):
    """
    The Quantity is some kind of physical quantity, e.g. temperature, humidity,
    """

    name = models.CharField(max_length=64, verbose_name=_("Name"))  # e.g. "temperature"
    abbreviation = models.CharField(
        max_length=64, verbose_name=_("Abbreviation")
    )  # e.g. "temp"
    symbol = models.CharField(
        max_length=64, blank=True, verbose_name=_("Symbol")
    )  # e.g. '°C', '%'
    description = models.TextField(blank=True, verbose_name=_("Comment"))
    # URLs to wikipedia, wikidata, ontologies etc. e.g.
    # https://www.wikidata.org/wiki/Q11466
    urls = models.TextField(blank=True, verbose_name=_("Reference URLs"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{} [{}]".format(self.name, self.symbol)

    class Meta:
        verbose_name_plural = "Quantities"


class Channel(models.Model):
    """
    All Datasources have one or more data channels.
    All Values are related to one Channel
    """

    datasource = models.ForeignKey(
        Datasource, related_name="channels", on_delete=models.CASCADE
    )
    quantity = models.ForeignKey(
        Quantity,
        blank=True,
        null=True,
        related_name="channels",
        on_delete=models.SET_NULL,
    )
    uniquename = models.CharField(
        max_length=64, blank=True, verbose_name=_("Unique name for unit")
    )  # e.g. "temp_1"
    name = models.CharField(
        max_length=64, null=True, blank=True, verbose_name=_("Name")
    )  # e.g. "Temperature"
    comment = models.CharField(
        max_length=256, blank=True, verbose_name=_("Comment")
    )  # e.g. "water"
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        try:
            return " | ".join([self.datasource.name, self.name, self.uniquename])
        except Exception:
            return f"Channel {self.pk}"


class Value(models.Model):
    """
    Single data element, which has a measuring timestamp, a data channel and a value.
    """

    time = models.DateTimeField(db_index=True)
    channel = models.ForeignKey(
        Channel, related_name="values", default=None, on_delete=models.CASCADE
    )
    value = models.FloatField()
    valid = models.BooleanField(default=True, verbose_name=_("Valid"))

    def __str__(self):
        return "{} {:.3f}".format(self.time, self.value)


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
    datasourcetype = Datasourcetype.objects.get(name=message["meta"]["dev-type"])
    datasource = datasourcetype.datasources.get(devid=message["meta"]["dev-id"])
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
