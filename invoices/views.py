# General imports
from django.shortcuts import render, get_object_or_404, reverse
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist

# Time imports
from datetime import *
from django.utils import timezone
from datetime import timedelta, date
import datetime
from dateutil.relativedelta import *

# Model imports
from .models import Invoice, InvoiceItem
from companies.models import Company
from bank.models import BankAccountEntry, BankAccount


# All Invoices View
@login_required
def all_invoices(request):
    """ A view to show all invoices, including sorting and search queries """

    all_invoices = Invoice.objects.all().order_by("date")
    all_companies = Company.objects.all().order_by("display_name")

    years_and_months = Invoice.objects.values('date')

    search_by_suplier = None
    search_by_customer = None
    search_by_year = None

    if request.GET:
        if 'suplier' in request.GET:
            search_by_suplier = request.GET['suplier']
        if 'customer' in request.GET:
            search_by_customer = request.GET['customer']
        if 'year' in request.GET:
            search_by_year = request.GET['year']
        if 'month' in request.GET:
            search_by_month = request.GET['month']
        if search_by_month != "":
            queries = Q(
                    suplier__registration_number__icontains=search_by_suplier
                ) & Q(
                    customer__registration_number__icontains=search_by_customer
                ) & Q(
                    date__year__icontains=search_by_year
                ) & Q(
                    date__month=search_by_month
                )
            all_invoices = all_invoices.filter(queries)
        else:
            queries = Q(
                    suplier__registration_number__icontains=search_by_suplier
                ) & Q(
                    customer__registration_number__icontains=search_by_customer
                ) & Q(
                    date__year__icontains=search_by_year
                )
            all_invoices = all_invoices.filter(queries)

    context = {
        'all_invoices': all_invoices,
        'all_companies': all_companies,
        'years_and_months': years_and_months,
    }

    return render(request, 'invoices/all_invoices.html', context)


# Invoice Details View
@login_required
def invoice_details(request, invoice_number):
    """ A view to return the invoice detail page """

    invoice = get_object_or_404(Invoice, invoice_number=invoice_number)
    customer_bank_account = get_object_or_404(BankAccount, bank_account_owner_com=invoice.customer)
    invoice_items = InvoiceItem.objects.filter(invoice=invoice)

    try:
        payment_info = BankAccountEntry.objects.get(
            bank_account=customer_bank_account,
            description=invoice.invoice_number,
        )
    except BankAccountEntry.DoesNotExist:
        payment_info = ""

    context = {
        'invoice': invoice,
        'payment_info': payment_info,
        'invoice_items': invoice_items,
    }

    return render(request, 'invoices/invoice_details.html', context)


# Add New Invoice
@login_required
def add_invoice(request):

    def is_ajax(request):
        return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'

    all_companies = Company.objects.all()

    if is_ajax(request):
        print(request)


# All WorkOrders View
