from django.contrib import admin
from .models import BankAccount, BankAccountEntry

# Register your models here.


class BankAccountEntryAdmin(admin.TabularInline):
    model = BankAccountEntry


class BankAccountAdmin(admin.ModelAdmin):
    inlines = (BankAccountEntryAdmin,)
    readonly_fields = ('bank_account_number', 'bank_account_saldo',)
    list_display = (
        'bank_account_owner_com',
        'bank_account_owner_pp',
        'bank_account_number',
        'bank_account_saldo'
    )

    ordering = ('bank_account_owner_pp', 'bank_account_owner_com', )


admin.site.register(BankAccount, BankAccountAdmin)
