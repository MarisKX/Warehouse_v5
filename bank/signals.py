# General Imports
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.shortcuts import get_object_or_404

# Model imports
from invoices.models import Invoice  # RetailSale, ConstructionInvoice
from .models import BankAccountEntry, BankAccount
# from taxes.models import TaxReport

# custom function imports
from home.today_calculation import today_calc


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


@receiver(post_save, sender=Invoice)
def create_transaction_entry(sender, instance, **kwargs):
    """
    Update order total on lineitem update/create
    """
    if instance.invoice_paid and instance.invoice_paid_confirmed == False:
        suplier_bank = get_object_or_404(BankAccount, bank_account_owner_com=instance.suplier)
        customer_bank = get_object_or_404(BankAccount, bank_account_owner_com=instance.customer)
        today = today_calc()
        BankAccountEntry.objects.create(
                bank_account=suplier_bank,
                date=today,
                description=instance.invoice_number,
                amount_plus=instance.amount_total_with_btw,
            )
        BankAccountEntry.objects.create(
                bank_account=customer_bank,
                date=today,
                description=instance.invoice_number,
                amount_minus=instance.amount_total_with_btw,
            )
        instance.invoice_paid_confirmed = True
        instance.save()
