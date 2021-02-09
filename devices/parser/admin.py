from django.contrib import admin

from parser.models import SensorType, Device


# Proper formatting for timestamps instead of "Oct. 27, 2020, 2:58 p.m." nonsense
def timestamp(obj):
    return obj.time.isoformat()


timestamp.admin_order_field = "time"
timestamp.short_description = "Timestamp"


def created_iso(obj):
    return obj.created_at.strftime("%Y-%m-%mT%H:%M:%S%z")


created_iso.admin_order_field = "created_at"
created_iso.short_description = "Created at"


class SensorTypeAdmin(admin.ModelAdmin):
    list_display = ("name", created_iso)


class DeviceAdmin(admin.ModelAdmin):
    list_display = ("devid", "name", created_iso)


admin.site.register(SensorType, SensorTypeAdmin)
admin.site.register(Device, DeviceAdmin)
