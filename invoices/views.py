# General imports
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Time imports
from datetime import *
from django.utils import timezone
from datetime import timedelta, date
import datetime
from dateutil.relativedelta import *

# Model imports
from .models import Invoice, InvoiceItem
from companies.models import Company


# All Invoices View
@login_required
def all_invoices(request):
    """ A view to show all invoices, including sorting and search queries """

    all_invoices = Invoice.objects.all().order_by("date")
    all_companies = Company.objects.all().order_by("display_name")

    years_and_months = Invoice.objects.values('date')

    if request.GET:
        if 'category' and 'subcategory' in request.GET:
            query_filter_category = request.GET['category']
            query_filter_subcategory = request.GET['subcategory']
            if query_filter_subcategory != "":
                queries = Q(
                    category_id=query_filter_category) & Q(
                    subcategory_id=query_filter_subcategory)
                products = products.filter(queries)
            else:
                queries = Q(
                    category__id__icontains=query_filter_category)
                products = products.filter(queries)

        if 'category' in request.GET:
            query_filter_category = request.GET['category']
            if query_filter_category != "":
                queries = Q(
                    category__id__icontains=query_filter_category)
                products = products.filter(queries)
            else:
                Product.objects.all().order_by("display_name")

    context = {
        'all_invoices': all_invoices,
        'all_companies': all_companies,
        'years_and_months': years_and_months,
    }

    return render(request, 'invoices/all_invoices.html', context)
