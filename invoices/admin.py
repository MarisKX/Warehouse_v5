from django.contrib import admin
from .models import (
    WorkOrder,
    WorkOrderItemRawMat,
    WorkOrderItemProduction,
    Invoice,
    InvoiceItem,
    )


class WorkOrderItemRawMatAdmin(admin.TabularInline):
    model = WorkOrderItemRawMat
    readonly_fields = (
        )
    list_display = (
        'work_order',
        'product',
        'quantity_in_units',
        'quantity_in_packages',
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


class InvoiceItemAdmin(admin.TabularInline):
    model = InvoiceItem
    readonly_fields = (
        )
    list_display = (
        'product',
        'quantity_in_units',
        'quantity_in_packages',
        'price',
        'lineitem_total',
        'btw',
        'lineitem_total_with_btw',
    )

    ordering = ('invoice',)


class InvoiceAdmin(admin.ModelAdmin):
    inlines = (InvoiceItemAdmin, )
    readonly_fields = (
        'invoice_number',
        'payment_term',
        'invoice_paid_confirmed',
        'amount_total',
        'btw_total',
        'amount_total_with_btw',
        )
    list_display = (
        'invoice_number',
        'suplier',
        'suplier_warehouse',
        'customer',
        'customer_warehouse',
        'date',
        'payment_term_options',
        'payment_term',
        'invoice_paid',
        'amount_total',
        'btw_total',
        'amount_total_with_btw',
    )

    ordering = ('invoice_number',)


admin.site.register(WorkOrder, WorkOrderAdmin)
admin.site.register(Invoice, InvoiceAdmin)