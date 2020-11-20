from django.contrib import admin
from observations.models import Channel, Datasource, Datasourcetype, Quantity, Value


# Proper formatting for timestamps instead of "Oct. 27, 2020, 2:58 p.m." nonsense
def timestamp(obj):
    return obj.time.isoformat()


timestamp.admin_order_field = "time"
timestamp.short_description = "Timestamp"


def created_iso(obj):
    return obj.created_at.strftime("%Y-%m-%mT%H:%M:%S%z")


created_iso.admin_order_field = "created_at"
created_iso.short_description = "Created at"


class DatasourcetypeAdmin(admin.ModelAdmin):
    list_display = ("name", created_iso)


class DatasourceAdmin(admin.ModelAdmin):
    list_display = ("devid", "name", created_iso)


class QuantityAdmin(admin.ModelAdmin):
    list_display = ("name", "symbol", "description", created_iso)


class ChannelAdmin(admin.ModelAdmin):
    list_display = ("name", "uniquename", "quantity", "datasource", created_iso)


class ValueAdmin(admin.ModelAdmin):
    list_display = (timestamp, "channel", "value")
    list_filter = ("channel", "value")


admin.site.register(Datasourcetype, DatasourcetypeAdmin)
admin.site.register(Datasource, DatasourceAdmin)
admin.site.register(Quantity, QuantityAdmin)
admin.site.register(Channel, ChannelAdmin)
admin.site.register(Value, ValueAdmin)
