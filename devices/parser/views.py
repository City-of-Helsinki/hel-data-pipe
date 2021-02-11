from rest_framework import viewsets

from .models import Device, SensorType
from .serializers import DeviceSerializer, SensorTypeSerializer


class SensorTypeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SensorType.objects.all()
    serializer_class = SensorTypeSerializer


class DeviceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Device.objects.all()
    serializer_class = DeviceSerializer
