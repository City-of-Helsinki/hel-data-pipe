from parser.models import Device, SensorType, RawMessage
from parser.management.commands import parse_data
from prettyjson import PrettyJSONWidget
from django.contrib.postgres.fields import JSONField

from django.contrib import admin


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


class RawMessageAdmin(admin.ModelAdmin):
    formfield_overrides = {
        JSONField: {'widget': PrettyJSONWidget(attrs={'initial': 'parsed'}) }
    }
    list_display = (created_iso, "devid", "status")
    readonly_fields = ('status',)

    def reprocess(modeladmin, request, queryset):
        """ Action function for reprocessing messages. """
        for message in queryset:
            print("status" + message.status)
            parse_data.process_message(message.data)

    reprocess.short_description = "Reprocess messages through parser"
    actions = [reprocess]

    # TODO: Exclude temporarily to prevent crashing due to binascii.Error: Incorrect padding
    exclude = ('data',)

admin.site.register(SensorType, SensorTypeAdmin)
admin.site.register(Device, DeviceAdmin)
admin.site.register(RawMessage, RawMessageAdmin)
