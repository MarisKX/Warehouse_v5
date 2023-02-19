from django.urls import path
from . import views

urlpatterns = [
    path('', views.all_invoices, name='all_invoices'),
    path('invoice_details/<invoice_number>/', views.invoice_details, name='invoice_details'),
]
