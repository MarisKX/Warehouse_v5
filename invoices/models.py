from django.db import models
from django.db.models import Sum
from django.shortcuts import get_object_or_404

from companies.models import Company
from warehouses.models import Warehouse
from products.models import Product, HandlingUnit
from citizens.models import Citizen


# WorkOrders and lineitems for them
class WorkOrder(models.Model):
    work_order_number = models.CharField(max_length=10, default='WO00001')
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name="company_work_order")
    warehouse_raw_materials = models.ForeignKey(
        Warehouse, on_delete=models.CASCADE, related_name="raw_warehouse")
    warehouse_production = models.ForeignKey(
        Warehouse,
        on_delete=models.CASCADE,
        related_name="production_warehouse")
    date = models.DateField(auto_now_add=False)
    enviroment_tax_on_workorder_total = models.DecimalField(
        max_digits=6, decimal_places=2, default=0.00)

    def __str__(self):
        return self.work_order_number

    def update_tax_wo_total(self):
        """
        Update grand total each time a line item is added,
        accounting for delivery costs.
        """
        self.enviroment_tax_on_workorder_total = (
            self.prod_work_order.aggregate(
                Sum('enviroment_tax_on_workorder')
                    )['enviroment_tax_on_workorder__sum'] or 0)
        super().save()


class WorkOrderItemRawMat(models.Model):
    work_order = models.ForeignKey(
        WorkOrder, null=False, blank=False,
        on_delete=models.CASCADE, related_name='raw_mat_work_order')
    product = models.ForeignKey(
        Product, null=False, blank=False,
        on_delete=models.CASCADE, related_name='raw_materials')
    quantity_in_units = models.IntegerField(null=False, blank=False, default=0)
    quantity_in_packages = models.IntegerField(null=False, blank=False, default=0)


class WorkOrderItemProduction(models.Model):
    work_order = models.ForeignKey(
        WorkOrder, null=False, blank=False,
        on_delete=models.CASCADE, related_name='prod_work_order')
    product = models.ForeignKey(
        Product, null=False, blank=False,
        on_delete=models.CASCADE, related_name='production')
    quantity_in_single_units = models.IntegerField(null=False, blank=False, default=0)
    quantity_in_units = models.IntegerField(null=False, blank=False, default=0)
    quantity_in_packages = models.IntegerField(null=False, blank=False, default=0)
    enviroment_tax_on_workorder = models.DecimalField(
        max_digits=6, decimal_places=2, default=0.00)

    def save(self, *args, **kwargs):
        """
        Override the original save method to set the lineitem total
        and update the order total.
        """
        self.enviroment_tax_on_workorder = (
            self.product.enviroment_tax_amount * self.quantity_in_single_units)
        if self.product.units_per_package > self.quantity_in_single_units:
            self.quantity_in_packages = 0
            self.quantity_in_units = self.quantity_in_single_units
            super().save(*args, **kwargs)
        elif self.quantity_in_single_units % self.product.units_per_package == 0:
            self.quantity_in_packages = self.quantity_in_single_units / self.product.units_per_package
            self.quantity_in_units = 0
            super().save(*args, **kwargs)
        else:
            print("Cannot divide in packages AND units")
            pass


# General Invoices and lineitems for them
class Invoice(models.Model):
    invoice_number = models.CharField(max_length=8, default='AA00001')
    suplier = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name="suplier")
    suplier_warehouse = models.ForeignKey(
        Warehouse, on_delete=models.CASCADE, related_name="suplier_warehouse")
    customer = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name="customer")
    customer_warehouse = models.ForeignKey(
        Warehouse, on_delete=models.CASCADE, related_name="customer_warehouse")
    date = models.DateField(auto_now_add=False)
    payment_term_choices = [
        ('7', '7 days'),
        ('14', '14 days'),
        ('21', '21 day'),
        ('30', '30 days'),
        ('60', '60 days'),
    ]

    payment_term_options = models.CharField(
        max_length=10, choices=payment_term_choices, default='14')
    payment_term = models.DateField(auto_now_add=False, null=True)
    invoice_paid = models.BooleanField(default=False)
    invoice_paid_confirmed = models.BooleanField(default=False)
    amount_total = models.DecimalField(
        max_digits=6, decimal_places=2, blank=True, null=True)
    btw_total = models.DecimalField(
        max_digits=6, decimal_places=2, blank=True, null=True)
    amount_total_with_btw = models.DecimalField(
        max_digits=6, decimal_places=2, blank=True, null=True)

    def update_invoice_total(self):
        """
        Update grand total each time a line item is added,
        accounting for delivery costs.
        """
        self.amount_total = self.lineitems.aggregate(
            Sum('lineitem_total'))['lineitem_total__sum'] or 0
        self.btw_total = (self.amount_total / 100) * 21
        self.amount_total_with_btw = self.amount_total + self.btw_total
        super().save()

    def __str__(self):
        return self.invoice_number


class InvoiceItem(models.Model):
    invoice = models.ForeignKey(
        Invoice, null=False, blank=False,
        on_delete=models.CASCADE, related_name='lineitems')
    product = models.ForeignKey(
        Product, null=False, blank=False, on_delete=models.CASCADE)
    quantity_in_units = models.IntegerField(null=False, blank=False, default=0)
    quantity_in_packages = models.IntegerField(null=False, blank=False, default=0)
    price = models.DecimalField(
        max_digits=6, decimal_places=2, default=0.00, blank=False)
    lineitem_total = models.DecimalField(
        max_digits=6, decimal_places=2, blank=True)
    btw = models.DecimalField(
        max_digits=6, decimal_places=2, blank=True, null=True)
    lineitem_total_with_btw = models.DecimalField(
        max_digits=6, decimal_places=2, blank=True, null=True)

    def save(self, *args, **kwargs):
        """
        Override the original save method to set the lineitem total
        and update the order total.
        """
        if self.quantity_in_units > 0:
            self.lineitem_total = self.price * self.quantity_in_units
        else:
            self.lineitem_total = self.price * self.quantity_in_packages
        self.btw = (self.lineitem_total / 100) * 21
        self.lineitem_total_with_btw = self.lineitem_total + self.btw
        super().save(*args, **kwargs)


# Transfer Orders
class TransferOrder(models.Model):
    to_number = models.CharField(max_length=10, default='TO00001')
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE,
        related_name="company_transfer_order")
    warehouse_from = models.ForeignKey(
        Warehouse, on_delete=models.CASCADE,
        related_name="transfer_order_from_warehouse")
    warehouse_to = models.ForeignKey(
        Warehouse, on_delete=models.CASCADE,
        related_name="transfer_order_to_warehouse")
    date = models.DateField(auto_now_add=False)

    def __str__(self):
        return self.to_number


class TransferOrderItem(models.Model):
    to_number = models.ForeignKey(
        TransferOrder, null=False, blank=False,
        on_delete=models.CASCADE,
        related_name='product_transfer_order_from')
    product = models.ForeignKey(
        Product, null=False, blank=False,
        on_delete=models.CASCADE,
        related_name='product_with_to')
    quantity_in_units = models.IntegerField(null=False, blank=False, default=0)


# Retail Sales
class RetailSale(models.Model):
    retail_sale_number = models.CharField(max_length=12, default='RT1')
    retailer = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name="retailer")
    retailer_warehouse = models.ForeignKey(
        Warehouse, on_delete=models.CASCADE, related_name="retailer_warehouse")
    customer = models.ForeignKey(
        Citizen, on_delete=models.CASCADE, related_name="customer")
    date = models.DateField(auto_now_add=False)
    retail_sale_paid = models.BooleanField()
    retail_sale_paid_confirmed = models.BooleanField()
    amount_total = models.DecimalField(
        max_digits=6, decimal_places=2, blank=True, null=True)
    btw_total = models.DecimalField(
        max_digits=6, decimal_places=2, blank=True, null=True)
    amount_total_with_btw = models.DecimalField(
        max_digits=6, decimal_places=2, blank=True, null=True)

    def update_retail_sale_total(self):
        """
        Update grand total each time a line item is added,
        accounting for delivery costs.
        """
        self.amount_total = self.retailitems.aggregate(
            Sum('retailitem_total'))['retailitem_total__sum'] or 0
        self.btw_total = (self.amount_total / 100) * 21
        self.amount_total_with_btw = self.amount_total + self.btw_total
        super().save()

    def __str__(self):
        return self.retail_sale_number


class RetailSaleItem(models.Model):
    retail_sale = models.ForeignKey(
        RetailSale, null=False, blank=False,
        on_delete=models.CASCADE, related_name='retailitems')
    product = models.ForeignKey(
        Product, null=False, blank=False, on_delete=models.CASCADE)
    quantity = models.IntegerField(null=False, blank=False, default=0)
    price = models.DecimalField(
        max_digits=6, decimal_places=2, default=0.00, blank=False)
    retailitem_total = models.DecimalField(
        max_digits=6, decimal_places=2, blank=True)
    btw = models.DecimalField(
        max_digits=6, decimal_places=2, blank=True, null=True)
    retailitem_total_with_btw = models.DecimalField(
        max_digits=6, decimal_places=2, blank=True, null=True)

    def save(self, *args, **kwargs):
        """
        Override the original save method to set the lineitem total
        and update the order total.
        """
        self.retailitem_total = self.price * self.quantity
        self.btw = (self.retailitem_total / 100) * 21
        self.retailitem_total_with_btw = self.retailitem_total + self.btw
        super().save(*args, **kwargs)
