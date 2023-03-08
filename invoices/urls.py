from django.urls import path
from . import views

urlpatterns = [
    path('', views.all_invoices, name='all_invoices'),
    path('invoice_details/<invoice_number>/', views.invoice_details, name='invoice_details'),
    path('bulk_retail_sale/', views.bulk_retail_sale, name='bulk_retail_sale'),
]
