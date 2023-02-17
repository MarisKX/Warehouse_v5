from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.shortcuts import get_object_or_404
from invoices.models import Invoice  # RetailSale, ConstructionInvoice
from .models import BankAccountEntry, BankAccount
# from taxes.models import TaxReport


@receiver(post_save, sender=BankAccountEntry)
def update_on_save(sender, instance, created, **kwargs):
    """
    Update bank account saldo on new entry update/create
    """
    instance.bank_account.update_bank_account_saldo()


@receiver(post_delete, sender=BankAccountEntry)
def update_on_delete(sender, instance, **kwargs):
    """
    Update bank account saldo on entry delete
    """
    instance.bank_account.update_bank_account_saldo()