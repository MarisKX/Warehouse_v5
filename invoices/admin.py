from django.contrib import admin
from .models import (
    WorkOrder,
    WorkOrderItemRawMat,
    WorkOrderItemProduction,
    Invoice,
    InvoiceItem,
    TransferOrder,
    TransferOrderItem,
    RetailSale,
    RetailSaleItem,
    ConstructionInvoice,
    ConstructionInvoiceItem,
    ConstructionInvoiceLabourCosts,
    )


# Workorders
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

    ordering = ('date',)


# General Invoices
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

    ordering = ('date',)


# Transfer Orders
class TransferOrderItemAdmin(admin.TabularInline):
    model = TransferOrderItem
    list_display = (
        'product',
        'quantity_in_units',
    )


class TransferOrderAdmin(admin.ModelAdmin):
    inlines = (TransferOrderItemAdmin, )
    readonly_fields = (
        'to_number',
    )
    list_display = (
        'to_number',
        'company',
        'warehouse_from',
        'warehouse_to',
        'date',
    )
    ordering = ('date', 'to_number',)


# Retail Sales
class RetailSaleItemAdmin(admin.TabularInline):
    model = RetailSaleItem
    readonly_fields = ('retailitem_total', 'btw', 'retailitem_total_with_btw',)


class RetailSaleAdmin(admin.ModelAdmin):
    inlines = (RetailSaleItemAdmin,)
    readonly_fields = (
        'retail_sale_number',
        'amount_total',
        'btw_total',
        'amount_total_with_btw',
    )
    list_display = (
        'retail_sale_number',
        'retailer',
        'customer',
        'date',
        'amount_total',
        'btw_total',
        'amount_total_with_btw',
    )
    ordering = ('date', 'retail_sale_number',)


# Construction Invocies
class ConstructionInvoiceItemAdmin(admin.TabularInline):
    model = ConstructionInvoiceItem
    readonly_fields = (
        'constructionitem_total',
        'btw',
        'constructionitem_total_with_btw',
    )


class ConstructionInvoiceLabourCostsAdmin(admin.TabularInline):
    model = ConstructionInvoiceLabourCosts
    readonly_fields = (
        'construction_labour_item_total',
        'btw',
        'construction_labour_item_total_with_btw',
    )


class ConstructionInvoiceAdmin(admin.ModelAdmin):
    inlines = (
        ConstructionInvoiceItemAdmin,
        ConstructionInvoiceLabourCostsAdmin,
    )
    readonly_fields = ('amount_total', 'btw_total', 'amount_total_with_btw',)
    list_display = (
        'c_invoice_number',
        'constructor',
        'build_customer',
        'date',
        'payment_term',
        'c_invoice_paid',
        'c_invoice_paid_confirmed',
        'amount_total',
        'btw_total',
        'amount_total_with_btw',
    )
    ordering = ('date', 'c_invoice_number',)


admin.site.register(WorkOrder, WorkOrderAdmin)
admin.site.register(Invoice, InvoiceAdmin)
admin.site.register(TransferOrder, TransferOrderAdmin)
admin.site.register(RetailSale, RetailSaleAdmin)
admin.site.register(ConstructionInvoice, ConstructionInvoiceAdmin)
