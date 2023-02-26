from django.urls import path
from . import views

urlpatterns = [
    path('', views.all_products, name='products'),
    path('product_details/<code>/', views.product_details, name='product_details'),
    path('product_details_in_pdf/<code>/', views.product_details_in_pdf, name='product_details_in_pdf'),
    path('add_category/', views.add_category, name='add_category'),
    path('add_product/', views.add_product, name='add_product'),
    path('handling_units/', views.all_handling_units, name='all_handling_units'),
]
