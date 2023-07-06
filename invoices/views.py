# General imports
from django.shortcuts import render, get_object_or_404, reverse
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.forms import inlineformset_factory

# Time imports
from datetime import *
from django.utils import timezone
from datetime import timedelta, date
import datetime
from dateutil.relativedelta import *

# Model imports
from .models import Invoice, InvoiceItem, RetailSale, RetailSaleItem
from companies.models import Company
from bank.models import BankAccountEntry, BankAccount
from products.models import Product, HandlingUnit
from citizens.models import Citizen
from warehouses.models import Warehouse

# Forms import
from .forms import InvoiceForm, InvoiceItemFormSet

# Custom functions import
from home.today_calculation import today_calc


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
    form = InvoiceForm()
    formset = InvoiceItemFormSet()

    def is_ajax(request):
        return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'

    if is_ajax(request):
        id_suplier = request.GET.get('id_suplier')
        id_customer = request.GET.get('id_customer')
        id_warehouse = request.GET.get("id_warehouse")
        if id_suplier is not None:

            company = get_object_or_404(Company, registration_number=id_suplier)
            id_suplier_warehouse = Warehouse.objects.filter(
                company=company,
                internal_warehouse=False
                ).order_by("display_name").values_list('id')
            suplier_warehouse = Warehouse.objects.filter(
                company=company,
                internal_warehouse=False
                ).order_by("display_name").values_list('display_name')

            return JsonResponse({
                "id_suplier_warehouse": list(id_suplier_warehouse),
                "suplier_warehouse": list(suplier_warehouse),
                })

        if id_customer is not None:

            company = get_object_or_404(Company, registration_number=id_customer)
            id_customer_warehouse = Warehouse.objects.filter(
                company=company,
                internal_warehouse=False
                ).order_by("display_name").values_list('id')
            customer_warehouse = Warehouse.objects.filter(
                company=company,
                internal_warehouse=False
                ).order_by("display_name").values_list('display_name')
            return JsonResponse({
                "id_customer_warehouse": list(id_customer_warehouse),
                "customer_warehouse": list(customer_warehouse),
                })

        if id_warehouse is not None:

            warehouse = get_object_or_404(Warehouse, id=id_warehouse)
            print(warehouse)
            hu_in_stock = HandlingUnit.objects.filter(location=warehouse)
            print(hu_in_stock)
            all_products_names_in_stock = []
            all_products_display_names_in_stock = []
            for hu in hu_in_stock:
                all_products_names_in_stock.append(hu.product.name)
                all_products_display_names_in_stock.append(
                    hu.product.display_name
                )
            products_names_in_stock = sorted(
                list(set(all_products_names_in_stock))
            )
            products_display_names_in_stock = sorted(
                list(set(all_products_display_names_in_stock))
            )
            product_ids = []
            for name in products_names_in_stock:
                try:
                    product = Product.objects.get(name=name)
                    product_ids.append(product.id)
                except Product.DoesNotExist:
                    # Handle the case when a product with the given name does not exist
                    product_ids.append(None)
            print(product_ids)
            print(products_names_in_stock)
            print(products_display_names_in_stock)

            return JsonResponse({
                "product_ids": product_ids,
                "products_display_names_in_stock": products_display_names_in_stock
                })

    if request.method == 'POST':
        form = InvoiceForm(request.POST)
        if form.is_valid():
            invoice = form.save()  # Save the invoice form and get the instance
            print(invoice.invoice_number)
            formset = InvoiceItemFormSet(request.POST, instance=invoice)
            if formset.is_valid():
                for form in formset:
                    if form.has_changed():
                        form.save()
                # Additional processing or redirect here
                        print("Object saved")
                return HttpResponse("Invoice created successfully")
            else:
                # Formset is not valid
                for form in formset:
                    if form.errors:
                        # Process and display the form errors
                        for field, error_list in form.errors.items():
                            for error in error_list:
                                print(f"Error in {field}: {error}")

    context = {
        'form': form,
        'formset': formset
    }

    return render(request, 'invoices/add_invoice.html', context)


# Bulk Retail Sale View
@login_required
def bulk_retail_sale(request):

    all_companies = Company.objects.all()
    all_products = Product.objects.all()

    def is_ajax(request):
        return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'

    if is_ajax(request):
        retailerCheck = request.GET.get('retailerCheck')
        if retailerCheck is not None:

            company = get_object_or_404(Company, registration_number=retailerCheck)
            retailer_warehouses_value = Warehouse.objects.filter(
                company=company,
                internal_warehouse=False
                ).order_by("display_name").values_list('name')
            retailer_warehouses = Warehouse.objects.filter(
                company=company,
                internal_warehouse=False
                ).order_by("display_name").values_list('display_name')
            print(retailer_warehouses)
            return JsonResponse({
                "retailer_warehouses_value": list(retailer_warehouses_value),
                "retailer_warehouses": list(retailer_warehouses),
                })

        bulk_retailer = request.GET.get('retailer')
        bulk_retailer_warehouse = request.GET.get('retailerWarehouse')
        bulk_product = request.GET.get('product')
        bulk_qty = int(request.GET.get('qty'))
        bulk_price = float(request.GET.get('price'))

        if bulk_retailer and bulk_product and bulk_qty is not None:

            all_citizens = Citizen.objects.all()
            retailer = get_object_or_404(Company, registration_number=bulk_retailer)
            retailerWarehouse = get_object_or_404(Warehouse, name=bulk_retailer_warehouse)
            product = get_object_or_404(Product, name=bulk_product)
            today = today_calc()
            retail_sales_invoices = []
            for citizen in all_citizens:
                RetailSale.objects.create(
                    retailer=retailer,
                    retailer_warehouse=retailerWarehouse,
                    customer=citizen,
                    date=today,
                    retail_sale_paid=False,
                    retail_sale_paid_confirmed=False,
                )
                created_retail_sale = RetailSale.objects.filter(
                    retailer=retailer,
                    retailer_warehouse=retailerWarehouse,
                    customer=citizen,
                    date=today,
                ).last()
                retail_sales_invoices.append(created_retail_sale.retail_sale_number)
                RetailSaleItem.objects.create(
                    retail_sale=created_retail_sale,
                    product=product,
                    quantity=bulk_qty,
                    price=bulk_price,
                )
                created_retail_sale.retail_sale_paid = True
                created_retail_sale.save()
            
            return JsonResponse({
                "retailInvoice": list(retail_sales_invoices),
                })

    context = {
        'all_companies': all_companies,
        'all_products': all_products,
    }

    return render(request, 'invoices/bulk_retail_sale.html', context)


# All WorkOrders View
