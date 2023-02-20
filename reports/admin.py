from django.contrib import admin
from .models import Report


# Register your models here.
class ReportAdmin(admin.ModelAdmin):
    readonly_fields = (
        'report_number',
        'gpd_from_invoices',
        'gpd_from_retail',
        'gpd_from_construction',
        'gpd_in_period',
        )
    list_display = (
        'date',
        'report_type',
        'report_year',
        'report_month',
        'report_number',
        'gpd_from_invoices',
        'gpd_from_retail',
        'gpd_from_construction',
        'gpd_in_period',
    )

    ordering = ('report_number',)


admin.site.register(Report, ReportAdmin)
