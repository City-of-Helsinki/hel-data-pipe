from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import DeviceViewSet, SensorTypeViewSet

router = DefaultRouter()
router.register(r"sensors", SensorTypeViewSet)
router.register(r"devices", DeviceViewSet)


urlpatterns = [
    path("", include(router.urls)),
]
