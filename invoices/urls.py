from django.urls import path
from . import views

urlpatterns = [
    path('', views.all_invoices, name='all_invoices'),
]
