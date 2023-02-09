from datetime import timedelta, date
from companies.models import Company
from django.shortcuts import get_object_or_404
from invoices.models import Invoice, WorkOrder, RetailSale, ConstructionInvoice
from .models import AppSettings


def extras(request):
    if request.user.is_authenticated:
        company = get_object_or_404(Company, owner=request.user)
        all_companies_with_stock = Company.objects.filter(
            warehouse=True).order_by('name')
        valid_settings = get_object_or_404(AppSettings, valid=True)
        actions_per_day = valid_settings.acions_per_day
        last_dates = []

        last_invoice = Invoice.objects.latest('date').date
        last_dates.append(str(last_invoice))

        last_workorder = WorkOrder.objects.latest('date').date
        last_dates.append(str(last_workorder))

        last_retail_sale = RetailSale.objects.latest('date').date
        last_dates.append(str(last_retail_sale))

        last_dates.sort()
        last_action_date = last_dates[-1]

        invoice_count = Invoice.objects.filter(date=last_action_date).count() or 0
        workorder_count = WorkOrder.objects.filter(date=last_action_date).count() or 0

        retail_count = RetailSale.objects.filter(date=last_action_date).count() or 0

        action_count = (
            invoice_count + workorder_count + retail_count
        )
        actions_left = actions_per_day - action_count

        if actions_left > 0:
             today = last_action_date
        else:
             today = last_action_date + timedelta(days=1)
        return {
            'company': company,
            'last_action_date': last_action_date,
            'actions_left': actions_left,
            'all_companies_with_stock': all_companies_with_stock,
            'valid_settings': valid_settings,
            'today': today,
        }
    else:
        all_companies_with_stock = Company.objects.filter(
            warehouse=True).order_by('name')
        return {
            'all_companies_with_stock': all_companies_with_stock,
        }
