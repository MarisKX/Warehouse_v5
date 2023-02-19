from django.contrib import admin
from .models import (
    Product,
    Category,
    SubCategory,
    HandlingUnit,
    HandlingUnitMovement,
    )

# Register your models here.


class SubCategoryAdmin(admin.TabularInline):
    model = SubCategory
    readonly_fields = ('name', )
    list_display = (
        'display_name',
        'name',
    )


class CategoryAdmin(admin.ModelAdmin):
    inlines = (SubCategoryAdmin,)
    readonly_fields = ('name', )
    list_display = (
        'display_name',
        'name',
    )


class ProductAdmin(admin.ModelAdmin):
    readonly_fields = (
        'code',
        'name',
        'units_per_lay',
        'units_per_palet',
        'packages_per_palet',
        )
    list_display = (
        'display_name',
        'name',
        'code',
        'category',
        'subcategory',
        'paletizable',
        'enviroment_tax_class',
        'enviroment_tax_amount',
        'expiry_end_date_terms',
        'expiry_end_date_cat',
        'units_per_package',
        'packages_per_lay',
        'lay_per_palet',
    )

    ordering = ('display_name',)


class HandlingUnitMovementAdmin(admin.TabularInline):
    model = HandlingUnitMovement
    readonly_fields = ('hu', )
    list_display = (
        'date',
        'doc_nr',
        'qty',
        'from_location',
        'from_hu',
        'to_location',
        'to_hu',

    )


class HandlingUnitAdmin(admin.ModelAdmin):
    inlines = (HandlingUnitMovementAdmin,)
    readonly_fields = (
        'hu',
        'active',
        'tht_warning_date',
        'tht',
        )
    list_display = (
        'hu',
        'manufacturer',
        'company',
        'location',
        'product',
        'qty',
        'qty_units',
        'batch_nr',
        'release_date',
        'tht_warning_date',
        'tht',
        'active',
    )

    ordering = ('hu',)


admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(HandlingUnit, HandlingUnitAdmin)
