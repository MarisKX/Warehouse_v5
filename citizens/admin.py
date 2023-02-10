from django.contrib import admin
from .models import Citizen


class CitizenAdmin(admin.ModelAdmin):
    readonly_fields = ('first_name', 'last_name', 'bsn_number', )
    list_display = (
        'first_name_display',
        'last_name_display',
        'bsn_number',
    )

    ordering = ('bsn_number',)


admin.site.register(Citizen, CitizenAdmin)
