# General Imports
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.shortcuts import get_object_or_404

# Model imports
from invoices.models import Invoice, RetailSale  # ConstructionInvoice
from .models import BankAccountEntry, BankAccount
from taxes.models import TaxReport
# from taxes.models import TaxReport

# custom function imports
from home.today_calculation import today_calc


# Bank Account saldo updates
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


# Signals from Invoices
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


# Signals from Tax reports
@receiver(post_save, sender=TaxReport)
def create_transaction_entry_taxes(sender, instance, **kwargs):
    """
    Update order total on lineitem update/create
    """
    if instance.taxes_paid and instance.taxes_paid_confirmed is False:
        tax_payer_bank = get_object_or_404(BankAccount,
                                           bank_account_owner_com=instance.company
                                           )
        gov_bank = get_object_or_404(BankAccount,
                                     bank_account_owner_com="4750100004"
                                     )
        # mun_bank = get_object_or_404(BankAccount,
        #                             bank_account_owner_com="4750100021"
        #                             )

        if instance.type == '2':
            BankAccountEntry.objects.create(
                    bank_account=tax_payer_bank,
                    description=f"" + instance.report_number + ", Nature Tax",
                    amount_minus=instance.amount,
                )
            BankAccountEntry.objects.create(
                    bank_account=gov_bank,
                    description=f"" + instance.report_number + ", Nature Tax",
                    amount_plus=instance.amount,
                )
        elif instance.type == "1":
            BankAccountEntry.objects.create(
                    bank_account=tax_payer_bank,
                    description=f"" + instance.report_number + ", BTW",
                    amount_minus=instance.amount,
                )
            BankAccountEntry.objects.create(
                    bank_account=gov_bank,
                    description=f"" + instance.report_number + ", BTW",
                    amount_plus=instance.amount,
                )
        instance.taxes_paid_confirmed = True
        instance.save()


# Signals from Retail sales
@receiver(post_save, sender=RetailSale)
def create_transaction_entry_for_retail_sales(sender, instance, **kwargs):
    """
    Update order total on lineitem update/create
    """
    if instance.retail_sale_paid and instance.retail_sale_paid_confirmed is False:
        retailer_bank = get_object_or_404(BankAccount, bank_account_owner_com=instance.retailer)
        BankAccountEntry.objects.create(
                bank_account=retailer_bank,
                description=instance.retail_sale_number,
                amount_plus=instance.amount_total_with_btw,
            )
        customer_bank = get_object_or_404(BankAccount, bank_account_owner_pp=instance.customer)
        BankAccountEntry.objects.create(
                bank_account=customer_bank,
                description=instance.retail_sale_number,
                amount_minus=instance.amount_total_with_btw,
            )
        instance.retail_sale_paid_confirmed = True
        instance.save()
