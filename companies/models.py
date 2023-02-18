from django.db import models
from django.core.validators import MaxValueValidator
from django.shortcuts import get_object_or_404
from django.db.models import Sum
from citizens.models import Citizen
from home.models import AppSettings
from home.letter_to_number_conv import letter_to_number


# Create your models here.
class Company(models.Model):

    class Meta:
        verbose_name_plural = 'Companies'

    owner = models.ForeignKey(Citizen, on_delete=models.CASCADE)
    name = models.CharField(max_length=254, blank=True, null=True)
    display_name = models.CharField(max_length=254, blank=True)
    warehouse = models.BooleanField(default=False)
    registration_number = models.PositiveIntegerField(
        blank=True,
        primary_key=True,
        default=1)
    invoice_prefix = models.CharField(max_length=2, blank=False, unique=True)
    manufacturer_code = models.IntegerField(default=0, blank=True)
    street_adress_1 = models.IntegerField(default=0, blank=True)
    street_adress_2 = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    post_code = models.CharField(max_length=6, blank=True)
    country = models.CharField(max_length=100, blank=True)
    employee_count = models.IntegerField(blank=True)
    total_salaries_cost = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        blank=True,
        null=True)
    total_bruto_salaries = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        blank=True,
        null=True)
    total_salary_vsaoi_dd = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        blank=True,
        null=True)
    total_salary_vsaoi_dn = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        blank=True,
        null=True)
    total_salary_iin = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        blank=True,
        null=True)
    total_salary_netto = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        blank=True,
        null=True)

    def __str__(self):
        return self.name

    def get_full_name(self):
        return self.full_name

    def get_house_number(self):
        return self.street_adress_1

    # Signal sent to companies-signals
    def salaries_total(self):
        """
        Update total salaries each time a employee is added,
        or his salary has been changed.
        """
        self.total_bruto_salaries = self.employer.aggregate(
            Sum('salary_brutto'))['salary_brutto__sum'] or 0
        self.total_salary_vsaoi_dd = self.employer.aggregate(
            Sum('salary_vsaoi_dd'))['salary_vsaoi_dd__sum'] or 0
        self.total_salary_vsaoi_dn = self.employer.aggregate(
            Sum('salary_vsaoi_dn'))['salary_vsaoi_dn__sum'] or 0
        self.total_salary_iin = self.employer.aggregate(
            Sum('salary_iin'))['salary_iin__sum'] or 0
        self.total_salary_netto = self.employer.aggregate(
            Sum('salary_netto'))['salary_netto__sum'] or 0
        super().save()

    def save(self, *args, **kwargs):
        """
        Override the original save method to set the company name
        if it hasn't been set already.
        """
        if self.registration_number == 1:
            company_count = Company.objects.all().count()
            self.registration_number = f"475010" + str(
                company_count + 1).zfill(4)
        self.manufacturer_code = letter_to_number(self.display_name)
        self.name = self.display_name.replace(" ", "_").lower()
        self.employee_count = Employees.objects.filter(company=self.registration_number).count()
        if self.employee_count > 0:
            self.total_salaries_cost = self.total_bruto_salaries + self.total_salary_vsaoi_dd
        else:
            self.total_salaries_cost = 0
        super().save(*args, **kwargs)


class Employees(models.Model):
    company = models.ForeignKey(
        Company,
        null=True,
        blank=False,
        on_delete=models.CASCADE,
        related_name='employer')
    name = models.ForeignKey(
        Citizen,
        null=True,
        blank=False,
        on_delete=models.CASCADE,
        related_name='employee')
    role = models.CharField(max_length=254, blank=True, null=True)
    salary_brutto = models.DecimalField(
        max_digits=8, decimal_places=2, blank=True, null=True)
    salary_vsaoi_dd = models.DecimalField(
        max_digits=8, decimal_places=2, blank=True, null=True)
    salary_vsaoi_dn = models.DecimalField(
        max_digits=8, decimal_places=2, blank=True, null=True)
    salary_iin = models.DecimalField(
        max_digits=8, decimal_places=2, blank=True, null=True)
    salary_netto = models.DecimalField(
        max_digits=8, decimal_places=2, blank=True, null=True)

    def save(self, *args, **kwargs):
        """
        Override the original save method to set the salary levels
        if it hasn't been set already.
        """
        latest_settings = get_object_or_404(AppSettings, valid=True)
        self.salary_vsaoi_dd = (self.salary_brutto / 100) * latest_settings.vsaoi_dd
        self.salary_vsaoi_dn = (self.salary_brutto / 100) * latest_settings.vsaoi_dn
        iin_calc = (
            (self.salary_brutto - self.salary_vsaoi_dn - latest_settings.no_iin_level) / 100) * latest_settings.iin_rate
        if iin_calc > 0:
            self.salary_iin = ((
                self.salary_brutto - self.salary_vsaoi_dn - latest_settings.no_iin_level) / 100) * latest_settings.iin_rate
        else:
            self.salary_iin = 0
        self.salary_netto = (
            self.salary_brutto - self.salary_vsaoi_dn - self.salary_iin)
        super().save(*args, **kwargs)
