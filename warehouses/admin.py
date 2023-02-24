from django.contrib import admin
from .models import Warehouse


# Register your models here.
class WarehouseAdmin(admin.ModelAdmin):
    readonly_fields = (
        'name',
        )
    list_display = (
        'company',
        'display_name',
        'name',
        'warehouse_code',
        'internal_warehouse',
    )

    ordering = ('name',)


admin.site.register(Warehouse, WarehouseAdmin)
