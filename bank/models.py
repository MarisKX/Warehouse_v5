from django.db import models
from django.db.models import Sum
from companies.models import Company
from citizens.models import Citizen

# Create your models here.


class BankAccount(models.Model):
    bank_account_owner_com = models.ForeignKey(Company, null=True, blank=True, on_delete=models.CASCADE, related_name='bank_account_owner_com')
    bank_account_owner_pp = models.ForeignKey(Citizen, null=True, blank=True, on_delete=models.CASCADE, related_name='bank_account_owner_pp')
    bank_account_number = models.CharField(max_length=18, blank=False, null=False, default="MK84MKCB...", primary_key=True)
    bank_account_saldo = models.DecimalField(max_digits=10, decimal_places=2, blank=False, null=False, default=0)

    def save(self, *args, **kwargs):
        """
        Override the original save method to set the bank account number
        if it hasn't been set already.
        """
        if self.bank_account_number == "MK84MKCB...":
            bank_accounts_count = BankAccount.objects.all().count()
            self.bank_account_number = "MK84MKCB101" + str(bank_accounts_count).zfill(7)
            super().save(*args, **kwargs)

    def update_bank_account_saldo(self):
        """
        Update bank account saldo each time the new transaction
        has been made.
        """
        self.bank_account_saldo = self.bank_account_entry.aggregate(Sum('saldo'))['saldo__sum'] or 0
        super().save()

    def __str__(self):
        return self.bank_account_number


class BankAccountEntry(models.Model):
    bank_account = models.ForeignKey('BankAccount', null=False, blank=False, on_delete=models.CASCADE, related_name='bank_account_entry')
    description = models.CharField(max_length=254, blank=True, null=True)
    amount_plus = models.DecimalField(max_digits=10, decimal_places=2, blank=False, null=False, default=0.00)
    amount_minus = models.DecimalField(max_digits=10, decimal_places=2, blank=False, null=False, default=0.00)
    saldo = models.DecimalField(max_digits=10, decimal_places=2, blank=False, null=False, default=0.00)

    def save(self, *args, **kwargs):
        """
        Override the original save method to set the lineitem total
        and update the order total.
        """
        self.amount_minus = self.amount_minus * -1
        self.saldo = float(self.amount_plus) + float(self.amount_minus)
        super().save(*args, **kwargs)
