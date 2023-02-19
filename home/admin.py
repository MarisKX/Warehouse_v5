from django.contrib import admin
from .models import AppSettings

# Register your models here.


class AppSettingsAdmin(admin.ModelAdmin):
    readonly_fields = ('settings_number',)
    list_display = (
        'settings_number',
        'acions_per_day',
        'valid',
        'valid_from',
        'valid_till',
        'no_iin_level',
        'enviroment_tax_base',
        'btw',
    )

    ordering = ('settings_number',)


admin.site.register(AppSettings, AppSettingsAdmin)