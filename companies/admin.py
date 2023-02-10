from django.contrib import admin
from .models import Company, Employees


# Register your models here.
class EmployeesAdmin(admin.TabularInline):
    model = Employees
    readonly_fields = (
        'salary_vsaoi_dd',
        'salary_vsaoi_dn',
        'salary_iin',
        'salary_netto',
        )
    list_display = (
        'company',
        'name',
        'salary_brutto'
    )

    ordering = ('name',)


class CompanyAdmin(admin.ModelAdmin):
    inlines = (EmployeesAdmin, )
    readonly_fields = ('name', 'total_bruto_salaries', 'total_salary_netto', )
    list_display = (
        'display_name',
        'invoice_prefix',
        'registration_number',
        'warehouse',
        'employee_count',
        # 'average_bruto_salary',
        'total_salaries_cost',
        'total_bruto_salaries',
        'total_salary_netto',

    )

    ordering = ('display_name',)


admin.site.register(Company, CompanyAdmin)