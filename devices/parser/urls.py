from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SensorTypeViewSet, DeviceViewSet


router = DefaultRouter()
router.register(r'sensors', SensorTypeViewSet)
router.register(r'devices', DeviceViewSet)


urlpatterns = [
    path('', include(router.urls)),
]
