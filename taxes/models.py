from django.db import models
from companies.models import Company


# Create your models here.

class TaxReport(models.Model):
    report_number = models.CharField(max_length=11, default='TR1')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="tax_payer")
    tax_date = models.DateField(auto_now_add=False)
    tax_type_choices = [
        ('1', 'BTW'),
        ('2', 'Nature Tax'),
        ('3', 'Company Income Tax'),
        ('4', 'VSAOI'),
        ('5', 'Citizen Income Tax'),
    ]
    type = models.CharField(max_length=10, choices=tax_type_choices, default='BTW')
    amount = models.DecimalField(max_digits=6, decimal_places=2, blank=False, null=False, default=0.00)
    taxes_paid = models.BooleanField()
    taxes_paid_confirmed = models.BooleanField()

    def __str__(self):
        return self.report_number

    def save(self, *args, **kwargs):
        """
        Override the original save method to set the subcategory name
        """
        if self.report_number == 'TR1':
            tax_report_count = TaxReport.objects.filter(company=self.company, type=self.type).count()
            self.report_number = 'TR' + self.company.invoice_prefix.upper() + self.type[0].upper() + str(tax_report_count + 1).zfill(6)
        super().save(*args, **kwargs)
