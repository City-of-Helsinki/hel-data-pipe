from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Channel, Datasource, Value
from .serializers import ChannelSerializer, DatasourceSerializer, ValueSerializer


class ChannelViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Channel.objects.all()
    serializer_class = ChannelSerializer

    def get_queryset(self):
        return Channel.objects.filter(datasource_id=self.kwargs["datasource_pk"])


class DatasourceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Datasource.objects.all()
    serializer_class = DatasourceSerializer


class ValueViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Value.objects.all().order_by("time")
    serializer_class = ValueSerializer

    def get_queryset(self):
        return Value.objects.filter(
            channel_id=self.kwargs["channel_pk"],
            channel__datasource_id=self.kwargs["datasource_pk"],
        )

    @action(detail=False)
    def latest(self, request, datasource_pk, channel_pk):
        latest_value = self.get_queryset().latest("time")
        serializer = self.get_serializer(latest_value, many=False)
        return Response(serializer.data)