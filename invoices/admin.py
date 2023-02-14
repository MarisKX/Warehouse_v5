from django.contrib import admin
from .models import WorkOrder, WorkOrderItemRawMat, WorkOrderItemProduction


class WorkOrderItemRawMatAdmin(admin.TabularInline):
    model = WorkOrderItemRawMat
    readonly_fields = (
        )
    list_display = (
        'work_order',
        'product',
        'quantity'
    )

    ordering = ('work_order',)


class WorkOrderItemProductionAdmin(admin.TabularInline):
    model = WorkOrderItemProduction
    readonly_fields = (
        'quantity_in_units',
        'quantity_in_packages',
    )
    list_display = (
        'work_order',
        'product',
        'quantity_in_single_units',
        'enviroment_tax_on_workorder',
    )

    ordering = ('work_order',)


class WorkOrderAdmin(admin.ModelAdmin):
    inlines = (WorkOrderItemRawMatAdmin, WorkOrderItemProductionAdmin,)
    readonly_fields = (
        'work_order_number',
        'enviroment_tax_on_workorder_total',
        )
    list_display = (
        'work_order_number',
        'company',
        'warehouse_raw_materials',
        'warehouse_production',
        'date',
        'enviroment_tax_on_workorder_total',

    )

    ordering = ('work_order_number',)


admin.site.register(WorkOrder, WorkOrderAdmin)
