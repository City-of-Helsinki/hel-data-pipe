from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import SensorType, Device
from .serializers import SensorTypeSerializer, DeviceSerializer


class SensorTypeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SensorType.objects.all()
    serializer_class = SensorTypeSerializer

class DeviceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Device.objects.all()
    serializer_class = DeviceSerializer
