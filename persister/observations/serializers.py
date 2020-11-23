from rest_framework import serializers

from .models import Channel, Datasource, Value


class ChannelSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Channel
        fields = ("id", "uniquename", "name")


class ValueSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Value
        fields = ("id", "time", "value")


class DatasourceSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Datasource
        fields = ("id", "devid", "name", "description", "lat", "lon")
