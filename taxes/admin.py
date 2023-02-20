from django.contrib import admin
from .models import TaxReport

# Register your models here.


class TaxReportAdmin(admin.ModelAdmin):
    readonly_fields = ('report_number', )
    list_display = (
        'report_number',
        'company',
        'tax_date',
        'type',
        'amount',
        'taxes_paid',
        'taxes_paid_confirmed',
    )


admin.site.register(TaxReport, TaxReportAdmin)
