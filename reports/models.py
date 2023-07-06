# General Imports
from django.db import models
from django.db.models import Sum
from django.shortcuts import get_object_or_404

# Model Imports
from citizens.models import Citizen
from companies.models import Company, Employees
from invoices.models import Invoice, WorkOrder, RetailSale, ConstructionInvoice
from bank.models import BankAccount, BankAccountEntry
from taxes.models import TaxReport
from warehouses.models import Warehouse

# Custom Imports
from home.today_calculation import today_calc


# Create your models here.
class Report(models.Model):

    class Meta:
        verbose_name_plural = 'Reports'

    date = models.DateField(auto_now_add=False)
    report_type_choices = [
        ('M', 'Monthly'),
        ('Y', 'Yearly'),
    ]
    report_type = models.CharField(
        max_length=16, choices=report_type_choices, default='M')
    month_choices = [
        (1, "January"), (2, "February"), (3, "March"),
        (4, "April"), (5, "May"), (6, "June"),
        (7, "July"), (8, "August"), (9, "September"),
        (10, "October"), (11, "November"), (12, "December"),
        ]
    report_year = models.IntegerField()
    report_month = models.IntegerField(
        choices=month_choices, blank=True, null=True)
    report_number = models.CharField(
        max_length=10, default=1, primary_key=True)
    gpd_from_invoices = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True)
    gpd_from_retail = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True)
    gpd_from_construction = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True)
    gpd_in_period = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return self.report_number

    def save(self, *args, **kwargs):
        """
        Override the original save method
        to calculate salaries and all taxes for period

        """
        if self.report_number == 1:
            self.date = today_calc()
            if self.report_type == "M":
                report_count = Report.objects.filter(
                    report_type='M').count()
                self.report_number = f"REP-MO-" + str(
                    report_count + 1).zfill(5)

                # Calculates GPD for period #####

                all_sales = Invoice.objects.filter(
                    date__year=self.report_year, date__month=self.report_month)
                invoice_gpd_dic = all_sales.aggregate(Sum('amount_total'))
                self.gpd_from_invoices = invoice_gpd_dic['amount_total__sum']

                all_retail_sales = RetailSale.objects.filter(
                    date__year=self.report_year, date__month=self.report_month)
                retail_gpd_dic = all_retail_sales.aggregate(
                    Sum('amount_total'))
                self.gpd_from_retail = retail_gpd_dic['amount_total__sum'] or 0

                all_construction = ConstructionInvoice.objects.filter(
                    date__year=self.report_year, date__month=self.report_month)
                construction_gpd_dic = all_construction.aggregate(
                    Sum('amount_total'))
                self.gpd_from_construction = (
                    construction_gpd_dic['amount_total__sum'] or 0)

                self.gpd_in_period = (
                    self.gpd_from_invoices + (
                        self.gpd_from_retail + self.gpd_from_construction))

                # Calculates and send to bank salaries for period #####

                all_employees = Employees.objects.all().order_by("name")
                all_companies = Company.objects.all().order_by("name")

                for e in all_employees:
                    employee_bank = get_object_or_404(
                        BankAccount, bank_account_owner_pp=e.name)
                    employer_bank = get_object_or_404(
                        BankAccount, bank_account_owner_com=e.company)
                    BankAccountEntry.objects.create(
                        bank_account=employee_bank,
                        date=self.date,
                        description="Salary " + str(self.report_month) + '/' + str(self.report_year) + " " + str(e.company.display_name),
                        amount_plus=e.salary_netto,
                        )
                    BankAccountEntry.objects.create(
                        bank_account=employer_bank,
                        date=self.date,
                        description="Salary " + str(
                            e.name.first_name_display) + " " + str(e.name.last_name_display) + ' - ' + str(
                                self.report_month) + '/' + str(
                                    self.report_year),
                        amount_minus=e.salary_netto,
                        )

                for company in all_companies:
                    company_bank = get_object_or_404(
                        BankAccount, bank_account_owner_com=company)
                    gov_bank = get_object_or_404(
                        BankAccount, bank_account_owner_com='4750100004')

                    # Employes and their taxes from salary#####

                    BankAccountEntry.objects.create(
                        bank_account=gov_bank,
                        date=self.date,
                        description="IIN " + str(company.display_name) + str(
                            self.report_month) + '/' + str(self.report_year),
                        amount_plus=company.total_salary_iin,
                        )
                    BankAccountEntry.objects.create(
                        bank_account=company_bank,
                        date=self.date,
                        description="IIN " + str(
                            self.report_month) + '/' + str(self.report_year),
                        amount_minus=company.total_salary_iin,
                        )
                    BankAccountEntry.objects.create(
                        bank_account=gov_bank,
                        date=self.date,
                        description="VSAOI " + str(company.display_name) + str(
                            self.report_month) + '/' + str(self.report_year),
                        amount_plus=(
                            company.total_salary_vsaoi_dd + (
                                company.total_salary_vsaoi_dn)),
                        )
                    BankAccountEntry.objects.create(
                        bank_account=company_bank,
                        date=self.date,
                        description="VSAOI " + str(
                            self.report_month) + '/' + str(self.report_year),
                        amount_minus=(
                            company.total_salary_vsaoi_dd + (
                                company.total_salary_vsaoi_dn)),
                        )

                    # Creates VSAOI Tax report

                    TaxReport.objects.create(
                        company=company,
                        tax_date=self.date,
                        type="4",
                        amount=(
                            company.total_salary_vsaoi_dd + (
                                company.total_salary_vsaoi_dn)),
                        taxes_paid=True,
                        taxes_paid_confirmed=True
                        )

                    # Creates IIN Tax report

                    TaxReport.objects.create(
                        company=company,
                        tax_date=self.date,
                        type="5",
                        amount=company.total_salary_iin,
                        taxes_paid=True,
                        taxes_paid_confirmed=True
                        )

                    # BTW Calculations #####

                    # Incomes ###

                    # Sales invoices
                    out_invoices = Invoice.objects.filter(
                        suplier=company,
                        date__year=self.report_year,
                        date__month=self.report_month
                        )
                    out_invoices_btw_dic = out_invoices.aggregate(
                        Sum('btw_total'))
                    btw_from_out_invoices = (
                        out_invoices_btw_dic['btw_total__sum'] or 0)

                    # Retail Sales invoices
                    out_retail_invoices = RetailSale.objects.filter(
                        retailer=company,
                        date__year=self.report_year,
                        date__month=self.report_month
                        )
                    out_retail_invoices_btw_dic = (
                        out_retail_invoices.aggregate(Sum('btw_total')))
                    btw_from_out_retail_invoices = (
                        out_retail_invoices_btw_dic['btw_total__sum'] or 0)

                    # Construction Invoices
                    constr_out_invoices = ConstructionInvoice.objects.filter(
                        constructor=company,
                        date__year=self.report_year,
                        date__month=self.report_month
                        )
                    constr_out_invoices_btw_dic = (
                        constr_out_invoices.aggregate(Sum('btw_total')))
                    btw_from_constr_out_invoices = (
                        constr_out_invoices_btw_dic['btw_total__sum'] or 0)

                    # Expenses ###

                    # Incoming Invoices
                    in_invoices = Invoice.objects.filter(
                        customer=company,
                        date__year=self.report_year,
                        date__month=self.report_month
                        )
                    in_invoices_btw_dic = in_invoices.aggregate(
                        Sum('btw_total'))
                    btw_from_in_invoices = (
                        in_invoices_btw_dic['btw_total__sum'] or 0)

                    # Incoming Construction Invoices
                    constr_in_invoices = ConstructionInvoice.objects.filter(
                        build_customer=company,
                        date__year=self.report_year,
                        date__month=self.report_month
                        )
                    constr_in_invoices_btw_dic = constr_out_invoices.aggregate(
                        Sum('btw_total'))
                    btw_from_constr_in_invoices = (
                        constr_in_invoices_btw_dic['btw_total__sum'] or 0)

                    total_btw_taxes_to_pay = (
                        btw_from_out_retail_invoices + (
                            btw_from_out_invoices + (
                                btw_from_constr_out_invoices - (
                                    btw_from_in_invoices - (
                                        btw_from_constr_in_invoices)))))

                    # Creates BTW tax report
                    if total_btw_taxes_to_pay == 0:
                        TaxReport.objects.create(
                            company=company,
                            tax_date=self.date,
                            type="1",
                            amount=total_btw_taxes_to_pay,
                            taxes_paid=True,
                            taxes_paid_confirmed=True
                            )
                    else:
                        TaxReport.objects.create(
                            company=company,
                            tax_date=self.date,
                            type="1",
                            amount=total_btw_taxes_to_pay,
                            taxes_paid=False,
                            taxes_paid_confirmed=False
                            )

                    # Calculations for nature tax from workorders #

                    all_work_orders = WorkOrder.objects.filter(
                        company=company,
                        date__year=self.report_year,
                        date__month=self.report_month
                        )
                    nature_tax_from_wo_dic = all_work_orders.aggregate(
                        Sum('enviroment_tax_on_workorder_total'))
                    nature_tax_from_wo = (
                        nature_tax_from_wo_dic['enviroment_tax_on_workorder_total__sum'] or 0)

                    if nature_tax_from_wo > 0:
                        TaxReport.objects.create(
                            company=company,
                            tax_date=self.date,
                            type="2",
                            amount=nature_tax_from_wo,
                            taxes_paid=False,
                            taxes_paid_confirmed=False
                            )
            else:
                report_count = Report.objects.filter(report_type='Y').count()
                self.report_number = f"REP-YE-" + str(
                    report_count + 1).zfill(5)

                all_sales = Invoice.objects.filter(date__year=self.report_year)
                invoice_gpd_dic = all_sales.aggregate(Sum('amount_total'))
                self.gpd_from_invoices = invoice_gpd_dic['amount_total__sum']

                all_retail_sales = RetailSale.objects.filter(
                    date__year=self.report_year)
                retail_gpd_dic = all_retail_sales.aggregate(
                    Sum('amount_total'))
                self.gpd_from_retail = retail_gpd_dic['amount_total__sum'] or 0

                all_construction = ConstructionInvoice.objects.filter(
                    date__year=self.report_year)
                construction_gpd_dic = all_construction.aggregate(
                    Sum('amount_total'))
                self.gpd_from_construction = construction_gpd_dic(
                    ['amount_total__sum'] or 0)

                self.gpd_in_period = self.gpd_from_invoices + (
                    self.gpd_from_retail + self.gpd_from_construction)

        super().save(*args, **kwargs)
