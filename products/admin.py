from django.contrib import admin
from .models import (
    Product,
    Category,
    SubCategory,
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
    readonly_fields = ('code', 'name', )
    list_display = (
        'display_name',
        'name',
        'code',
        'category',
        'subcategory',
        'enviroment_tax_class',
        'enviroment_tax_amount',
        'expiry_end_date_terms',
        'expiry_end_date_cat',
    )

    ordering = ('display_name',)


admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)
