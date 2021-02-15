from django.urls import include, path
from rest_framework_nested import routers

from .views import ChannelViewSet, DatasourceViewSet, ValueViewSet

# Nested routing to get route like /datasources/:id/channels/:id/values
router = routers.SimpleRouter()
router.register(r"datasources", DatasourceViewSet)

datasources_router = routers.NestedSimpleRouter(
    router, r"datasources", lookup="datasource"
)
datasources_router.register(r"channels", ChannelViewSet, basename="datasource-channels")

channels_router = routers.NestedSimpleRouter(
    datasources_router, r"channels", lookup="channel"
)
channels_router.register(r"values", ValueViewSet, basename="datasource-channel-values")

urlpatterns = [
    path("", include(router.urls)),
    path("", include(datasources_router.urls)),
    path("", include(channels_router.urls)),
]
